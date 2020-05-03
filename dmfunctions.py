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
    char.hp -= amount


def heal(char, amount=None):
    if amount is None:
        char.heal()
    else:
        char.heal(amount)


# Should be moved to item.py
def printcontents(item):
    for thing in item.storage:
        print(item.name + ": " + thing.name)
        printcontents(thing)


# def showitems(character):
#     for item in character.gear and character.inventory:
#         print(item.name)
#         printcontents(item)


def levelUp(char):
    char.levelUp()


# TODO: create faction lists from factions dict, pass to savecharacters
def load():
    """builds factions, a dictionary of (name,list)s. don't use mid-session"""
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
                # This is why I used a dictionary constructor ;)
                factions[faction].append(character.Character(data))

    return factions


def savecharacters(characters):
    """characters is a list of character objects"""
    for char in characters:

        # characters must have a faction
        if char.faction == (None or ""):
            print(char.name + " has no faction, and wasn't saved.")

        # create directory if it doesn't exist
        elif not os.path.exists(".\\factions\\" + char.faction):
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


# def savefactions(factions):
#     for key,value in factions.iteritems():
#         savecharacters(value)

# TODO: dual wield penalty, input sanitization
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
    if weapon.dexorstr == "strength":
        mod = attacker.strmod
    elif weapon.dexorstr == "dexterity":
        mod = attacker.dexmod
    elif weapon.dexorstr == "finesse":
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
