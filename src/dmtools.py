import character
import resources
import random
from statistics import NormalDist
import json
import os


def roll(dice=1, die=20):
    """custom roll, takes (dice)d(die)"""
    return sum([random.randint(1, die) for x in range(dice)])


def roll3d20mid():
    """mid variance standard roll"""
    return sorted([random.randint(1, 20) for x in range(3)])[1]


def roll3d6():
    """low variance standard roll"""
    return sum([random.randint(1, 6) for x in range(3)])


def roll7d2():
    """lowest variance standard roll"""
    return sum([random.randint(1, 2) for x in range(7)])


def disadvantage(dice=1, die=20):
    """rolls disadvantage for (dice)d(die)"""
    return min(roll(dice, die), roll(dice, die))


def advantage(dice=1, die=20):
    """rolls advantage for (dice)d(die)"""
    return max(roll(dice, die), roll(dice, die))


def create(full=False, **kwargs):
    """Character creation function

    Args:
        **kwargs (dict, optional): Optionally include attributes as kwargs. Defaults to {}.
        full (bool, optional): If you want to edit each attribute, full=True. Defaults to False.
    """

    # if you want full control you can edit each value
    if not full:
        defaults = list(character.characterCreationDefaults.items())[:7]
    else:
        defaults = list(character.characterCreationDefaults.items())

    for key, value in defaults:
        # manually enter each value that data doesn't have
        if key not in kwargs:
            # only way to restart a loop iteration is to nest an infinite loop and break it on a success
            # thank you python
            while True:
                try:
                    s = input(f'{key} ? ')
                    if s == '':
                        continue
                    # dynamic type casting
                    # thank you C
                    kwargs[key] = type(value)(s)
                    print(f'{key} data assigned')
                    break

                except (TypeError, ValueError):
                    print(" invalid parameter")

    return character.Character(kwargs)

# TODO: expanded 5e longrest implementation
def longrest(*characterLists):
    """pass lists of character objects to reset their hp"""
    for characterList in characterLists:
        for character in characterList:
            character.heal()


def groupInitiative(*characterLists):
    """generates initiative rolls from lists of characters.

    Returns:
        list: of (initiative roll, character name) tuples
    """
    # it's this but faster
    # order = []
    # for characterList in characterLists:
    #     for character in characterList:
    #         order.append((character.initiative(), character.name))
    # order = sorted(order, reverse=True)
    # return order

    return sorted(
        [(character.initiative(), character.name) for characterList in characterLists for character in characterList]
    , reverse=True)


def setDc(successOdds, dice=3, die=6, roundDown=True):
    """returns the DC of a % success chance

    Args:
        successOdds (int): the 0-99 chance of action success.
        dice (int, optional): number of dice to roll. Defaults to 3.
        die (int, optional): faces per die. Defaults to 6.
        roundDown (bool, optional): floors the DC -- for lower variance rolls. Defaults to True.

    Returns:
        int: the corresponding DC
    """
    successOdds /= 100

    # calculate mean, standard deviation, and then DC

    # calculate mean. dice*die is max, dice is min, dice*(die+1) is max+min
    mean = (dice * (die + 1)) / 2

    # calculate standard deviation via discrete uniform variance formula
    # (n^2 - 1) / 12
    dieVariance = (die ** 2 - 1) / 12
    diceVariance = dieVariance * dice
    stDev = diceVariance ** 0.5

    # calculate a DC using the inverse cumulative distribution function
    dc = NormalDist(mu=mean, sigma=stDev).inv_cdf(successOdds)

    # rotate around the 10.5 mean (17 becomes 4, 11 becomes 10, etc)
    # alternatively: dc = dice*(die+1) - dc
    dc = -(dc - mean) + mean

    if roundDown:
        # casting floats to ints truncates in python. don't have to import math
        return f"{int(dc)} (rounded down from {dc})"
    return f"{round(dc)} (rounded from {dc})"

def hurt(char, amount):
    char.hurt(amount)


def heal(char, amount=None):
    if amount is None:
        char.heal()
    else:
        char.heal(amount)


def levelUp(char):
    char.levelUp()


def dismember(char, atMost=2):
    """permanently randomly decrease a character's attribute

    Args:
        char (character Obj): to dismember
        atMost (int, optional): maximum possible value to decrease by. Defaults to 2.
    """
    char.attributes[random.randrange(0,len(char.attributes))] -= random.randint(1,atMost)
    char.update()

def randomNames(n, *namefiles, threshold=3):
    """spits out random names from namefiles

    Args:
        n (int): number of random names to return
        *namefiles (strings): e.g. 2 namefiles produces 'john smith', 1 yields 'john'
        threshold (int, optional): above threshold, switches to O(n) space algorithm. Defaults to 2.

    Returns:
        tuple: of ('random name' 'for each' 'namefile used') strings
    """

    # use a faster space-less algorithm (crediting Python Cookbook) if few names are needed
    if n <= threshold:
        names = ['' for x in range(n)]
        for idx,_ in enumerate(names):
            for namefile in namefiles:
                lineIndex = 0
                selectedLine = None
                with open(namefile, 'r') as f:
                    while True:
                        line = f.readline()
                        if not line: # readline() returns '' at EOF
                            break
                        lineIndex += 1
                        # first line has a 1/1 chance of being selected
                        # the nth line has a 1/n chance of overwriting previous selection
                        if random.uniform(0, lineIndex) < 1:
                            selectedLine = line

                # (add spaces between firstname nthname lastname)
                names[idx] += selectedLine.rstrip() + ' '
            names[idx].rstrip() # remove trailing space
        return names
        # while rstrip() is slower than name[:-1], it's O(1)

    # otherwise, store all file data in lists for faster accesses
    else:
        # build a list of lists of random names from each file
        namefileListList = []
        for namefile in namefiles:
            namefileList = []
            with open(namefile, 'r') as f:
                for line in f:
                    namefileList.append(line) # name whitespace and trailing newline preserved
            namefileListList.append(namefileList) # better to rstrip on assignment

        # now actually create and return the random names
        # i could've simply created a names list, and edited each value with enumerate
        # but i'm practicing comprehension nesting. this is starting to become readable
        return tuple((' '.join(
            choice(namefileList).rstrip() for namefileList in namefileListList
            ) for henchman in range(n)))


def henchmen(n, *namefiles, attributes={}, faction=[]):
    """generates henchmen for use in combat encounters

    Args:
        n (int): number of henchmen
        namefiles (str, optional): text files to source random character names from
        attributes (dict, optional): a data dict containing elements for character construction
        faction (list, optional): a faction list to put henchmen inside

    Returns:
        (list): faction list, containing all the henchmen
    """
    # a "def foo(*args=(args,here)):" syntax is sorely needed
    if not namefiles:
        namefiles = tuple(('firstnames.txt','lastnames.txt'))

    # create list of henchmen,
    characters = [character.Character(attributes) for x in range(n)]
    # generate random names,
    names = randomNames(n, *namefiles)
    # name the characters
    for idx in range(n):
        characters[idx].name = names[idx]
    # add them to the faction,
    faction += characters
    # send it
    return faction


# 3rd iteration of this function. I finally did n-depth recursion,
# and deprecated the faction class for easy json serialization
def load():
    """builds factions, a nested dict eventually containing lists of character Objs.
    ***WILL OVERWRITE IF USED MID-SESSION***
    """

    # can't really use isinstance() here :(
    # TODO: this stopped working?
    if 'factions' in globals() or 'factions' in locals():
        print("load() was used while factions var exists; exiting to prevent overwrite")
        return

    sep = os.sep

    # recursive function to both load characters and populate the root factions dict
    def populateFactions(rootList, cd, files):
        # rootList is from walker e.g. ['sgc', 'sg13']. cd is the current dictionary
        parentDict = rootList.pop() # e.g. 'sgc' being "sg13"'s parent

        # base case: rootList is empty after being popped. now dict can be populated
        if not rootList:
            faction = []
            for fileStr in files:
                with open(fileStr, 'r') as f:
                    faction.append(character.Character(json.load(f)))
            cd[parentDict] = faction
            return

        # otherwise, keep traversing
        if parentDict not in cd:
            cd[parentDict] = {}
        populateFactions(rootList=rootList, cd=cd[parentDict], files=files)

    # generator yielding file locations
    #                               root:           dirs       files
    # walker output looks like ['./factions'], ['sgc','trust'], []
    walker = ((root, dirs, files) for root,dirs,files in os.walk(f".{sep}factions"))

    # first yield is sort of like a dir head (it has no root), so it gets its own statement
    factions = {key:{} for key in next(walker)[1]} # factions is currently e.g. {'sgc':{}, 'trust':{}}

    for root, dirs, files in walker:
        if files:
            files = [root+sep+fileStr for fileStr in files]

            # TODO os.walk's python list is the wrong data structure here. a linked list makes the most sense, I think.
            # a deque import is costly but scales well. realistically this doesn't matter

            # root.split(sep) looks like [".", "factions", "<faction1>", "<faction2>", ...]
            # [::-1] reverses the list; populateFactions can rootList.pop() efficiently
            # [:1:-1] slices out the first 2 (junk) elements from the original unreversed list
            faction = populateFactions(rootList=root.split(sep)[:1:-1], cd=factions, files=files)

    return factions


# i can't think of any real improvements to the save function now
def save(factions=None):
    """writes all character data to local jsons

    Args:
        factions (dict): arbitrarily nested dicts eventually containing lists full of character objects
    """
    sep = os.sep # separator character e.g. '/' or '\\' (repr('\\')->'\') on windows
    def getCharactersFromDicts(iterable, path=f'.{sep}factions{sep}'):
        # put every nested dict on the stack
        if isinstance(iterable, dict):
            for key, value in iterable.items(): # e.g. path="./factions/sgc/" first
                getCharactersFromDicts(value, path=(path+key+sep))

        # we've hit a faction list
        if isinstance(iterable, list):
            for char in iterable:
                # create directories if they don't exist
                if not os.path.exists(path):
                    os.makedirs(path)

                # character faction should be updated on each save
                # it is purely cosmetic at this point, though
                # this ultimately does "./factions/x/y/z" -> "/x/y/z"
                char.faction = sep+sep.join(path.split(sep)[2:]).replace('\\','/') # for windows

                # write character to file
                # open(, 'w+') makes the file if it doesn't exist. no more pathlib import
                # TODO: why did blair ignore encoding errors?
                with open(f'{path}{char.name}.json', 'w+', encoding='utf-8', errors='ignore') as f:
                    json.dump(char.getJSON(), f)

    if factions == None:
        factions = factions
    getCharactersFromDicts(factions)


# from my original 2019 codebase
# i've improved a lot since then. i gave it a facelift, but
# it's a lot less readable. it works, so i'm not touching it
def attack(attacker, defender, weapon=None, distance=0, cover=0):
    """attacker rolls against defender with weapon from distance

    Args:
        attacker (Character): Character attacking
        defender (Character): Character defending
        weapon (Weapon): Attacker's weapon
        distance (int, optional): Attack distance. Defaults to 0.
        cover (int, optional): % defender is covered. Defaults to None.
    """
    # factoring distance
    if distance == 0:
        distancemod = 1
    else:
        # 2 is arbitrary
        distancemod = 1 - (distance / weapon.range) ** 2
        if distancemod < 0:
            distancemod = 0

    # factoring cover
    if cover == 0:
        covermod = 0
    else:
        covermod = int(cover // 25)

    # fetch weapon
    if weapon is None:
        if attacker.rightHand is None:
            if attacker.leftHand is None:
                return "no valid attacker wep" # TODO: unarmed combat
            else:
                weapon = attacker.leftHand
        else:
            weapon = attacker.rightHand

    # weapon mods to hit
    mod = 0
    if weapon.proficiency == "strength":
        mod = attacker.strmod
    elif weapon.proficiency == "dexterity":
        mod = attacker.dexmod
    elif weapon.proficiency == "finesse":
        mod = max(attacker.strmod, attacker.dexmod)

    # hit calculation
    hitcalc = roll3d6() + mod

    # dual wield penalty
    if attacker.leftHand is not None and attacker.rightHand is not None:
        hitcalc -= 2

    # qc penalty for long range weapons
    if weapon.cqcpenalty > 0 and distance > 3:
        hitcalc -= 2 * weapon.cqcpenalty
        print("close combat weapon penalty applied")

    # does the attack hit?
    if hitcalc > (defender.AC + covermod):
        # damage calculation
        damage = (
            round(
                roll(2, weapon.damage // 2) * distancemod
            )
        )

        print(f"{attacker.name} rolled {hitcalc} to hit {defender.name} for {damage}")

        defender.hurt(totalDamage=damage)

        print(f"{defender.name} is at {defender.hp} health")

    else:
        print("miss!")
