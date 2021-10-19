import character
import item
import random
from statistics import NormalDist
from copy import deepcopy
import json
import os
import rolls

sep = os.sep

# muuuch better than previous. now with easy default value input and extensible modes
def create(mode=0, **kwargs):
    """Character creation function

    Args:
        mode (int, optional): level of detail. Defaults to 0.
        kwargs (dict, optional): to include on creation. Defaults to {}.
    """
    def handleInput(key, defaultsDict=character.defaults):
        # TODO P2: this doesn't handle invalid races/classes properly because 
        # dict membership checking happens in the character constructor
        while True:
            try:
                value = input(f'{key} <<< ')
                # blank input uses the character.default value
                if value == '':
                    return defaultsDict[key]
                # must dynamically cast input string to appropriate type before returning
                return type(defaultsDict[key])(value)
            except ValueError:
                print(f" invalid entry")

    data = {} # this gets populated and then returned
    basics = ['name', 'race', 'clas', 'faction', 'level']
    stats = {'attributes':character.defaults['attributes'], 'skills':character.defaults['skills']}

    # stuffing the basic values into attributes
    for basic in basics:
        data[basic] = handleInput(basic)

    # optionally manulaly edit character attributes and skills
    if mode:
        for statDictName,statDict in stats.items():
            data[statDictName] = {
                statName:handleInput(statName,defaultsDict=statDict) for statName,statValue in statDict.items()
                }

    # at the end, insert kwargs, overwriting any defaults
    for key,value in kwargs.items():
        data[key] = value

    return character.Character(data)


# TODO P3: expanded 5e longrest implementation
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
    return sorted(
        [(character.initiative(), character.name) for characterList in characterLists for character in characterList]
    , reverse=True)

def setDc(successOdds, dice=rolls.dice, die=rolls.die, roundDown=True):
    """returns the DC of a % success chance

    Args:
        successOdds (int): the 0-99 chance of action success.
        dice (int, optional): number of dice to roll. Defaults to rolls.dice.
        die (int, optional): faces per die. Defaults to rolls.die.
        roundDown (bool, optional): floors the DC -- for lower variance rolls. Defaults to True.

    Returns:
        int: the corresponding DC
    """
    successOdds /= 100

    # calculate a DC using the inverse cumulative distribution function
    dc = NormalDist(mu=rolls.diceMean, sigma=rolls.diceStDev).inv_cdf(successOdds)

    # rotate around the 10.5 mean (17 becomes 4, 11 becomes 10, etc)
    # alternatively: dc = dice*(die+1) - dc
    dc = -(dc - rolls.diceMean) + rolls.diceMean

    if roundDown:
        # casting floats to ints truncates in python. don't have to import math
        return f"{int(dc)} (rounded down from {dc})"
    return f"{round(dc)} (rounded from {dc})"

def oddsNum(dc, dice=rolls.dice, die=rolls.die):
    """return odds of succeeding a dice check

    Args:
        dc (int): Dice check to pass/fail
        dice (int, optional): Number of dice. Defaults to 3.
        die (int, optional): Number of sides per die. Defaults to 6.

    Returns:
        [str]: Percent chance of success
    """
    odds = NormalDist(mu=rolls.diceMean, sigma=rolls.diceStDev).cdf(dc)
    percentSuccess = 100 - int(round(odds, 2) * 100)

    return f"DC of {dc} rolling {dice}d{die}: {percentSuccess}% success"
    # in python 2, (1 + erf(x/root2))/2 can be substituted for normaldist.cdf

# alias commands
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
    list(char.attributes.values())[random.randrange(0,len(char.attributes))] -= random.randint(1,atMost)
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

    # use a faster space-less algorithm (crediting Python Cookbook) if fewer names are needed
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
        return tuple((' '.join(
            random.choice(namefileList).rstrip() for namefileList in namefileListList
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
    # a "def foo(*args=(args,here)):" syntax is needed
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

# TODO P1: test the hell out of this
# TODO P3: this smells awful. i think item's constructor could use a rework. it also does 2 things instead of 1
# the solution here might just be to collapse weapon and armor types into the item class. armor especially
# barely offers functionality beyond the base class
def loadItem(itemAttrs):
    """(recursively) loads an item in memory

    Args:
        itemAttrs (dict or str): an attr dict to manually create an item with, or a filename str to load from

    Returns:
        Item: loaded
    """
    if type(itemAttrs) == dict:
        itemJSON = itemAttrs
    elif type(itemAttrs) == str:
        with open(f'.{sep}items{sep}'+itemAttrs) as f:
            itemJSON = json.load(f)
    # this order actually matters a lot, because some weapons have bonusAC
    # range key check determines the item to load is a weapon,
    if 'range' in itemJSON:
        itemObj = item.Weapon(*itemJSON.values())
        itemObj.storage = [loadItem(*itemJSON.values()) for item in itemObj.storage]
        return itemObj
    # bonusAC determines it's armor,
    if 'bonusAC' in itemJSON:
        itemObj = item.Armor(*itemJSON.values())
        itemObj.storage = [loadItem(*itemJSON.values()) for item in itemObj.storage]
        return itemObj
    # otherwise it's a normal item
    itemObj = item.Item(*itemJSON.values())
    itemObj.storage = [loadItem(item) for item in itemObj.storage]
    return itemObj

# 4th iteration of this function. characters are now populated with gear
# os.walk's python list is the wrong data structure here. a linked list makes the most sense, I think.
# a deque import is costly but scales well. realistically this doesn't matter
def load():
    """builds factions, a nested dict eventually containing lists of character Objs.
    ***WILL OVERWRITE IF USED MID-SESSION***
    """

    # can't really use isinstance() here :(
    # TODO P2: this broke
    if 'factions' in globals() or 'factions' in locals():
        print("load() was used while factions var exists; exiting to prevent overwrite")
        return

    # recursive function to both load characters (with items) and populate the root factions dict
    def populateFactions(rootList, cd, files):
        # rootList is from walker e.g. ['sg13', 'sgc']. cd is the current dictionary
        outerDict = rootList.pop() # sgc will equal {'sg13':_, ...} so it's "outer"

        # base case: rootList is empty after being popped. now dict can be populated
        if not rootList:
            faction = []
            for fileStr in files:
                with open(fileStr) as f:
                    # convert each serialized character into an object,
                    charObj = character.Character(json.load(f))
                    # convert each serialized item into an object,
                    charObj.slots = {slot:loadItem(item) if item is not None else None \
                        for slot,item in charObj.slots.items()}
                    # update the character to calculate weight & speed
                    charObj.update()
                    # add the character to the faction,
                    faction.append(charObj)
            # send faction to dict
            cd[outerDict] = faction
            return

        # otherwise, keep traversing
        if outerDict not in cd:
            cd[outerDict] = {}
        populateFactions(rootList=rootList, cd=cd[outerDict], files=files)

    # generator yielding file locations
    #                               root:           dirs       files
    # walker output looks like ['./factions'], ['sgc','trust'], []
    walker = ((root, dirs, files) for root,dirs,files in os.walk(f".{sep}factions"))

    # first yield is sort of like a dir head (it has no root), so it gets its own statement
    factions = {key:{} for key in next(walker)[1]} # factions is currently e.g. {'sgc':{}, 'trust':{}}
    #    (dirs unused)
    for root, _, files in walker:
        if files:
            files = [root+sep+fileStr for fileStr in files]

            # root.split(sep) looks like [".", "factions", "<faction1>", "<faction2>", ...]
            # [::-1] reverses the list; populateFactions can rootList.pop() efficiently
            # [:1:-1] slices out the first 2 (junk) elements from the original unreversed list
            populateFactions(rootList=root.split(sep)[:1:-1], cd=factions, files=files)

    return factions


def save(factions=None):
    """writes all character data to local jsons

    Args:
        factions (dict): arbitrarily nested dicts eventually containing lists of character objects
    """
    def getCharactersFromDicts(iterable: list or dict, path=f'.{sep}factions{sep}'):
        # put every nested dict on the stack
        if isinstance(iterable, dict):
            for key, value in iterable.items(): # e.g. path="./factions/sgc/" first
                getCharactersFromDicts(value, path=(path+key+sep))

        # encountered a charObj list
        if isinstance(iterable, list):
            for charObj in iterable:
                # save a copy of the character, so the session can continue if needed
                charCopy = deepcopy(charObj)
                # create directories if they don't exist
                if not os.path.exists(path):
                    os.makedirs(path)

                # character faction should be updated on each save
                # it is purely cosmetic at this point, though
                # this slicing ultimately does ".\\factions\\x/y/z/" -> "/x/y/z"
                charCopy.faction = sep+sep.join(path.split(sep)[2:-1]).replace('\\','/') # for windows

                # write character to file
                with open(f'{path}{charCopy.name}.json', 'w+', encoding='utf-8', errors='ignore') as f:
                    json.dump(charCopy.getJSON(), f)

    # TODO P3: implement this
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
        weapon (Weapon): Attacker's weapon. Defaults to None.
        distance (int, optional): Attack distance. Defaults to 0.
        cover (int, optional): % defender is covered. Defaults to None.
    """
    # factoring distance
    if distance == 0:
        distanceMod = 1
    else:
        # 2 is arbitrary
        distanceMod = 1 - (distance / weapon.range) ** 2
        if distanceMod < 0:
            distanceMod = 0

    # factoring cover
    if cover == 0:
        coverMod = 0
    else:
        coverMod = int(cover // 25)

    # fetch weapon
    if weapon is None:
        if attacker.slots['rightHand'] is None:
            if attacker.slots['leftHand'] is None:
                return "no valid attacker wep" # TODO: unarmed combat
            else:
                weapon = attacker.slots['leftHand']
        else:
            weapon = attacker.slots['rightHand']

    # weapon mods to hit
    mod = 0
    if weapon.proficiency == "strength":
        mod = attacker.strMod
    elif weapon.proficiency == "dexterity":
        mod = attacker.dexMod
    elif weapon.proficiency == "finesse":
        mod = max(attacker.strMod, attacker.dexMod)

    # hit calculation
    hitcalc = roll3d6() + mod

    # dual wield penalty
    if attacker.slots['leftHand'] is not None and attacker.slots['rightHand'] is not None:
        hitcalc -= 2

    # qc penalty for long range weapons
    if weapon.cqcpenalty > 0 and distance > 3:
        hitcalc -= 2 * weapon.cqcpenalty
        print("close combat weapon penalty applied")

    # does the attack hit?
    if hitcalc > (defender.AC + coverMod):
        # damage calculation
        damage = (
            round(
                rolls.roll(2, weapon.damage // 2) * distanceMod
            )
        )

        print(f"{attacker.name} rolled {hitcalc} to hit {defender.name} for {damage}")

        defender.hurt(totalDamage=damage)

        print(f"{defender.name} is at {defender.hp} health")

    else:
        print("miss!")
