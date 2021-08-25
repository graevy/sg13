import character
import resources
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
    order = []
    for characterList in characterLists:
        for character in characterList:
            order.append((character.initiative(), character.name))
    order = sorted(order, reverse=True)
    return order


def setDc(successOdds=None, dice=3, die=6, roundDown=True):
    """returns the DC of a % success chance

    Args:
        successOdds (int, optional): the 0-99 chance of action success. Defaults to None.
        dice (int, optional): number of dice to roll. Defaults to 3.
        die (int, optional): faces per die. Defaults to 6.
        roundDown (bool, optional): floors the DC -- use this for lower variance rolls. Defaults to True.

    Returns:
        int: the corresponding DC
    """
    if successOdds is None:
        successOdds = int(input(r"What % success do you want? (int): ").strip())

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


# so this actually worked first try. no new testing needed :)
def nameCharacter(*namefiles):
    """generates a random character name from files of random names

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
        # but uniform(0,n) can equal n in most other cases
        # so this algorithm can't TypeError

    return name.strip() # to remove the trailing space


def henchmen(n, attributes={}, faction=[], *namefiles):
    """generates henchmen for use in combat encounters

    Args:
        n (int): number of henchmen
        attributes (dict, optional): a data dict containing elements for character construction
        faction (list, optional): a faction list to put henchmen inside
        namefiles (str, optional): text files to source random character names from

    Returns:
        (list): a list containing all the henchmen
    """
    idx = 0
    for henchman in range(n):
        if namefiles:
            name = nameCharacter(*namefiles)
        else:
            idx += 1
            name = f'NPC {idx}'

        faction.append(character.Character(attributes, name=name))

    return faction


# TODO: second pass at this. doesn't do n-depth yet, and 
# i'm thinking a faction class is better to use here
def load():
    """builds factions, a dict of {name,characterList}s. don't use mid-session"""

    # can't really use isinstance() here :(
    if 'factions' in globals() or 'factions' in locals():
        print("load() was used while factions var exists; exiting to prevent overwrite")
        return
    else:
        factions = {}

    # root.split("/") looks like [".", "factions", "faction1", "faction2", etc], so pruning it here saves a headache
    walker = ((root.split("/")[2:], dirs, files) for root,dirs,files in os.walk("./factions"))

    # first yield is sort of like a file header for the directory, so it gets its own statement
    for elem in next(walker)[1]:
        factions[elem] = {}
        # factions is currently e.g. {'sgc':{}, 'trust':{}}

    # TODO: this is sloppy, even with the syntax cleaned up.
    # it's a good candidate for recursion
    for elem in walker:
        root, dirs, files = elem
        # "if the root isn't just a single faction name, e.g. ['sgc', 'sg14']:"
        if len(root) > 1:
            # set a key, value pair. factions['sgc']['sg14'] = []
            factions[root[0]][root[-1]] = []
            # now add each character to the faction list
            for charFile in files: #     sgc        sg13 
                with open(f"./factions/{root[0]}/{root[-1]}/{charFile}", "r", encoding="utf-8") as f:
                    factions[root[0]][root[-1]].append(character.Character(json.load(f)))

    return factions


# i can't think of any real improvements to the save function now other than custom objects
# works in linux, haven't tested on windows B)
def save(factions=None):
    """writes all character data to local jsons

    Args:
        factions (dict): arbitrarily nested dicts eventually containing a faction list full of character objects
    """
    def getCharactersFromDicts(iterable, path='./factions/'):
        # put every nested dict on the stack
        if isinstance(iterable, dict):
            for key, value in iterable.items(): # e.g. path="./factions/sgc/" first
                getCharactersFromDicts(value, path=(f"{path}{key}/"))

        # we've hit a faction list
        if isinstance(iterable, list):
            for char in iterable:
                # create directories if they don't exist
                if not os.path.exists(path):
                    os.makedirs(path)

                # character faction should be updated on each save
                # it is purely cosmetic at this point, though
                # path[10:-1] does "./factions/xyz/" -> "/xyz"
                char.faction = path[10:-1]

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


# old character creation functions

# def createCharacter(data):
#     return character.Character(data)

# def manuallyCreateCharacter():
#     """walks through character creation manually for each variable"""

#     data = character.characterCreationDefaults

#     print("leave blank to use default value")
#     for k, v in character.characterCreationDefaults.items():
#         try:
#             s = input(str(k)+' ? ')
#             if s == '':
#                 continue
#             # Dynamic type casting is apparently supported by python, by just slapping a class object in front of another object
#             data[k] = type(v)(s)
#             print(k+' data assigned')
#         except (TypeError, ValueError):
#             # TODO: continue statement, but from the same iteration instead of the next
#             print(" invalid parameter")

#     print(data)
#     return character.Character(data)
