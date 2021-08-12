import character
import resources
from random import randint,uniform
import json
import os
from pathlib import Path


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


def create(mode='basic', **kwargs):
    """Character creation function

    Args:
        **kwargs (dict, optional): Optionally include kwargs. Defaults to {}.
        mode (str, optional): 'full' for every value, 'basic' for important values. Defaults to 'basic'.
    """

    # if you want full control you can edit each value
    if mode == 'full':
        things = list(character.characterCreationDefaults.items())
    if mode == 'basic':
        things = list(character.characterCreationDefaults.items())[:9]
    else:
        return "invalid mode parameter"

    for k,v in things:
        # manually enter each value that data doesn't have
        if k not in kwargs.keys():
            # only way to restart a loop iteration is to nest an infinite loop and break it on a success
            # thank you python
            while True:
                try:
                    s = input(str(k)+' ? ')
                    if s == '':
                        continue
                    # Dynamic type casting is apparently supported by python
                    # you just slap a class object in front of another object
                    # thank you C
                    kwargs[k] = type(v)(s)
                    print(k+' data assigned')
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


def initiative(*characterLists):
    """generates initiative rolls from lists of characters.
    send (list)(factions.values()) to use every character, for example

    Returns:
        list: a list of (initiative roll, character name) tuples
    """
    order = []
    for characterList in characterLists:
        for character in characterList:
            order.append(character.initiative(), character.name)
    return sorted(order)


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


# TODO
def henchmen(n, attributes, faction=[], *namefiles):
    for henchman in range(n):
        # this is an entire section dedicated to naming npcs extensibly
        # completely untested
        if namefiles:
            name = ''
            for namefile in namefiles:
                # cool algorithm I stole from sof
                line_num = 0
                selected_line = ''
                with open(namefile, 'r') as f:
                    while True:
                        line = f.readline()
                        if not line: break
                        line_num += 1
                        # here's the meat. it's equally likely to spit out each item
                        # even without knowing the total number of items
                        # so we get O(n/2) instead of O(2n) by running over the file twice, and
                        # O(1) space complexity instead of O(n) by not saving file metadata
                        if random.uniform(0, line_num) < 1:
                            selected_line = line

                name += selected_line.strip() + ' '
            name = name.strip()
        else:
            name = 'NPC'

        faction.append(character.Character(attributes))

    return faction

def savefactions(factions):
    """Saves all factions' characters' jsons to local dir

    Args:
        factions (dict): a dictionary of {faction:characterlist}s
    """

    for factionName, faction in factions.items():
        for char in faction:

            # if this somehow happens it needs to get fixed on write
            if char.faction != factionName:
                char.faction = factionName

            # create directory if it doesn't exist
            if not os.path.exists(".\\factions\\" + char.faction):
                os.makedirs(".\\factions\\" + char.faction)

            # create file if it doesn't exist
            Path(
                ".\\factions\\" + char.faction + "\\" + char.name + ".json"
            ).touch()

            # write
            with open(
                f".\\factions\\{char.faction}\\{char.name}.json",
                "w+",
                encoding="utf-8",
                # lol
                errors="ignore",
            ) as f:
                json.dump(char.getJSON(), f)

# TODO: support for complex faction names eg "sgc/sg13". currently thinking about using os.walk or recursion
# def load():
#     """builds factions, a dict of {name,characterList}s. don't use mid-session"""

#     if 'factions' in locals() or 'factions' in globals():
#         print("load() was used while factions var exists; exiting to prevent overwrite")
#         return
#     else:
#         factions = {}

#     for root, faction, character in os.walk("./factions"):

#         factions[faction] = []

#         with open(
#             "./factions/" + faction + "/" + char,
#             "r",
#             encoding="utf-8",
#             errors="ignore",
#         ) as f:
#             data = json.load(f)
#             factions[faction].append(character.Character(data))

#     return factions

def load():
    """builds factions, a dict of {name,characterList}s. don't use mid-session"""

    if 'factions' in locals() or 'factions' in globals():
        print("load() was used while factions var exists; exiting to prevent overwrite")
        return
    else:
        factions = {}

    for faction in os.listdir("./factions"):

        factions[faction] = []

        for char in os.listdir("./factions/" + faction):

            with open(
                "./factions/" + faction + "/" + char,
                "r",
                encoding="utf-8",
                errors="ignore",
            ) as f:
                data = json.load(f)
                factions[faction].append(character.Character(data))

    return factions


def attack(attacker, defender, weapon=attacker.rightHand, distance=0, cover=0):
    """attacker rolls against defender with weapon from distance

    Args:
        attacker (Character): Character attacking
        defender (Character): Character defending
        weapon (Weapon): Attacker's weapon
        distance (int, optional): Attack distance. Defaults to 0.
        cover (int, optional): % defender is covered. Defaults to None.
    """
    # factoring in distance

    if distance == 0:
        distancemod = 1
    else:
        distance = int(distance)
        # 2 is an arbitrary exponent to scale down weapon efficacy at range. change if needed
        distancemod = 1 - (distance / weapon.range) ** 2
        if distancemod < 0:
            distancemod = 0

    # factoring in cover
    if cover == 0:
        covermod = 0
    else:
        cover = int(cover)
        covermod = cover // 25

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


###################################################
# Not sure if I want to use this implementation yet

# def savecharacter(character):
#     # create directory if it doesn't exist
#     if not os.path.exists(".\\factions\\" + character.faction):
#         os.makedirs(".\\factions\\" + character.faction)

#     # create file if it doesn't exist
#     Path(
#         ".\\factions\\" + character.faction + "\\" + character.name + ".json"
#     ).touch()

#     # write
#     with open(
#         ".\\factions\\" + character.faction + "\\" + character.name + ".json",
#         "w+",
#         encoding="utf-8",
#         errors="ignore",
#     ) as f:
#         json.dump(character.getJSON(), f)

# def savefaction(faction):
#     for char in faction.values():
#         savecharacter(char)

# def savefactions(factions)
#       for faction in factions.values():
#           savefaction(faction)
###################################################


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