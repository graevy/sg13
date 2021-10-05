import character
import resources
import faction
from random import randint,uniform
from statistics import NormalDist
import json
import os


def roll(dice=1, die=20):
    """custom roll, takes (dice)d(die)"""
    return sum([randint(1, die) for x in range(dice)])


def roll3d20mid():
    """mid variance standard roll"""
    return sorted([randint(1, 20) for x in range(3)])[1]


def roll3d6():
    """low variance standard roll"""
    return sum([randint(1, 6) for x in range(3)])


def roll7d2():
    """lowest variance standard roll"""
    return sum([randint(1, 2) for x in range(7)])


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
                    # Dynamic type casting is apparently supported by python
                    # you just slap a class object in front of another object
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

    return sorted([(character.initiative(), character.name) for characterList in characterLists for character in characterList], reverse=True)


def setDc(successOdds, dice=3, die=6, roundDown=True):
    """returns the DC of a % success chance

    Args:
        successOdds (int): the 0-99 chance of action success.
        dice (int, optional): number of dice to roll. Defaults to 3.
        die (int, optional): faces per die. Defaults to 6.
        roundDown (bool, optional): floors the DC -- use this for lower variance rolls. Defaults to True.

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


def dismember(char):
    char.attributes[randint(0,5)] -= randint(1,2)
    char.update()


def nameCharacter(*namefiles):
    """generates a random character name from files of random names,
    best for naming one character. use nameCharacters for multiple

    Returns:
        str: the full name
    """
    name = ''
    for namefile in namefiles:
        # cool algorithm courtesy of the Python Cookbook
        # it's equally likely to spit out each item
        # even without knowing the total number of items
        # still linear time complexity, but
        # O(1) space by not loading file data
        lineIndex = 0
        selectedLine = None
        with open(namefile, 'r') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                lineIndex += 1
                # the cool part
                # first name has a 1/1 chance of being selected
                # the nth name has a 1/n chance of overwriting previous selection
                if uniform(0, lineIndex) < 1:
                    selectedLine = line

        # (spaces between firstname nthname lastname)
        name += selectedLine.strip() + ' '

        # after too much reading i learned that uniform(0,1) can't ever equal 1
        # but uniform(0,n) can equal n in most other cases, varying by machine
        # so this algorithm can't TypeError

    return name[:-1] # remove the trailing space
    # i actually tested the timing on name[:-1] vs name.rstrip() using my timing module
    # slicing the last character off is something like 15% faster on average,
    # until you get out to names longer than ~40 characters
    # slicing saved something like 90ns on average. i am drunk with power


# i thought i was smart by using the cool space-less algorithm for naming,
# but really, loading everything into memory is faster for most batch operations
# so now it's unnecessarily complicated. there's a lesson here
def nameCharacters(characters, *namefiles):
    """space-complex algorithm to name large groups of characters from namefiles

    Args:
        characters (list): of character objects to name
    """

    # store all possible names in lists
    namefileTuplesList = []
    for namefile in namefiles:
        entry = []
        idx = 0
        with open(namefile, 'r') as f:
            while True:
                idx += 1
                line = f.readline()
                if not line:
                    break
                entry.append(line)
        namefileTuplesList.append((idx, entry))

    # name all characters from those lists
    # using enumerate to auto-generate names if not provided
    for idx,character in enumerate(characters):
        name = ''
        if namefiles:
            for namefileLength,namefileArray in namefileTuplesList:
                name += namefileArray[random.randint(0,namefileLength)] + ' '
            character.name = name[:-1]
        else:
            character.name = f"NPC {idx+1}"


# TODO: new implementation untested
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
    idx = 0
    # use nameCharacter if n is 1
    if n  == 1:
        faction.append(character.Character(attributes, name=nameCharacter(*namefiles)))
        return faction
    # use nameCharacters otherwise
    else:
        # create list of henchmen,
        characters = [character.Character(attributes) for x in range(n)]
        # name them all,
        nameCharacters(characters, *namefiles)
        # add them to the faction,
        faction += characters
        # send it
        return faction


# 3rd iteration of this function. I finally did n-depth,
# and deprecated the faction class for json serialization
def load():
    """builds factions, a dict of {name,characterList}s. don't use mid-session"""

    # can't really use isinstance() here :(
    if 'factions' in globals() or 'factions' in locals():
        print("load() was used while factions var exists; exiting to prevent overwrite")
        return

    sep = os.sep

    # TODO: list probably not ideal data structure for this
    def populateFactions(dirList, cd, files):
        # dirList is the directory list from root from walker. cd is the current dictionary
        # base case: load everything into directory
        if len(dirList) < 2:
            faction = []
            for fileStr in files:
                with open(fileStr, 'r') as f:
                    faction.append(character.Character(json.load(f)))
            cd[dirList[0]] = faction
            return
        # otherwise, keep traversing
        if dirList[0] not in cd:
            cd[dirList[0]] = {}
        populateFactions(dirList=dirList[1:], cd=cd[dirList[0]], files=files)

    walker = ((root, dirs, files) for root,dirs,files in os.walk(f".{sep}src{sep}factions"))

    # first yield is sort of like a file header for the directory (it has no root), so it gets its own statement
    factions = {key:{} for key in next(walker)[1]} # factions is currently e.g. {'sgc':{}, 'trust':{}}

    for root, dirs, files in walker:
        if files:
            files = [root+sep+fileStr for fileStr in files]
            # root.split(sep) looks like [".", "src", "factions", "faction1", "faction2", etc]
            faction = populateFactions(dirList=root.split(sep)[3:], cd=factions, files=files)

    return factions


# i can't think of any real improvements to the save function now
def save(factions=None):
    """writes all character data to local jsons

    Args:
        factions (dict): arbitrarily nested dicts eventually containing lists full of character objects
    """
    sep = os.sep
    def getCharactersFromDicts(iterable, path=f'.{sep}src{sep}factions{sep}'):
        # put every nested dict on the stack
        if isinstance(iterable, dict):
            for key, value in iterable.items(): # e.g. path="./src/factions/sgc/" first
                getCharactersFromDicts(value, path=(path+key+sep))

        # we've hit a faction list
        if isinstance(iterable, list):
            for char in iterable:
                # create directories if they don't exist
                if not os.path.exists(path):
                    os.makedirs(path)

                # character faction should be updated on each save
                # it is purely cosmetic at this point, though
                # path[10:-1] does "./src/factions/xyz" -> "/xyz"
                char.faction = path[14:-1].replace('\\','/') # i hate windows

                # write character to file
                # open(, 'w+') makes the file if it doesn't exist. no more pathlib import
                # TODO: why did blair ignore encoding errors in the original function?
                with open(f'{path}{char.name}.json', 'w+', encoding='utf-8', errors='ignore') as f:
                    json.dump(char.getJSON(), f)

    # not tested
    if factions == None:
        factions = eval('factions', globals())
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
