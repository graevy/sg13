import character
import resources
from random import randint
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

def createCharacter(data):
    return character.Character(data)

def manuallyCreateCharacter():
    """walks through character creation manually for each variable"""

    data = character.characterCreationDefaults

    print("leave blank to use default value")
    for k, v in character.characterCreationDefaults.items():
        try:
            s = input(str(k)+' ? ')
            if s == '':
                continue
            # Dynamic type casting is apparently supported by python, by just slapping a class object in front of another object
            data[k] = type(v)(s)
            print(k+'data assigned')
        except (TypeError, ValueError):
            # TODO: continue statement, but from the same iteration instead of the next
            print("invalid parameter")

    print(data)
    return character.Character(data)


# TODO: expanded 5e longrest implementation
def longrest(characters):
    """pass a list of character objects to reset their hp"""
    for char in characters:
        char.heal()


def groupinitiative(characters):
    order = []
    for char in characters:
        order.append({char.name, char.initiative()})
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
                ".\\factions\\" + char.faction + "\\" + char.name + ".json",
                "w+",
                encoding="utf-8",
                errors="ignore",
            ) as f:
                json.dump(char.getJSON(), f)

# TODO: support for complex faction names eg "sgc/sg13". currently thinking about using os.walk
# def load():
#     """builds factions, a dict of {name,characterList}s. don't use mid-session"""

#     if 'factions' in (locals() or globals()):
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

    if 'factions' in (locals() or globals()):
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


# TODO: dual wield penalty
def attack(attacker, defender, weapon, distance=0, cover=None):
    """master attack function"""
    # factoring in distance
    distance = input("distance? blank=ignore")

    if distance == "":
        distance = 0
        distancemod = 1

    distance = int(distance)
    # 2 is an arbitrary exponent to scale down weapon efficacy at range. change if needed
    distancemod = 1 - (distance / weapon.range) ** 2
    if distancemod < 0:
        distancemod = 0

    # factoring in cover
    cover = input("cover? 25, 50, or 75; blank=0")

    if cover == "":
        cover = 0
        covermod = 0

    cover = int(cover)
    covermod = cover / 25

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

    # qc penalty for long range weapons
    if weapon.cqcpenalty > 0 and distance > 3:
        hitcalc -= 2 * weapon.cqcpenalty
        print("close combat weapon penalty applied")

    if hitcalc > (defender.AC + covermod):
        # damage calculation
        damage = (
            round(
                (
                    randint(1, weapon.damage // 2)
                    + randint(1, weapon.damage // 2)
                )
            )
            * distancemod
        )

        print(
            attacker.name
            + " rolled "
            + str(hitcalc)
            + " to hit "
            + defender.name
            + " for "
            + str(damage)
            + "!"
        )

        defender.hurt(totalDamage=damage)

        print(defender.name + " is at " + str(defender.hp) + " health.")

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