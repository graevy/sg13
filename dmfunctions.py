import character
import resources
from random import randint
import json, jsonpickle
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
    for character in characters:
        character.hp = character.maxhp
        character.temphp = 0


def groupinitiative(characters):
    order = []
    for character in characters:
        order.append({character.name, character.rolliniative})
    return sorted(order)


def hurt(character, amount):
    character.hp -= amount


def heal(character, amount=9999):
    if character.hp + amount > character.maxhp:
        character.hp = character.maxhp
    else:
        character.hp += amount


def printcontents(item):
    for thing in item.storage:
        print(item.name + ": " + thing.name)
        printcontents(thing)


# def showitems(character):
#     for item in character.gear and character.inventory:
#         print(item.name)
#         printcontents(item)


def levelUp(character):

    character.level += 1

    # level attributes
    character.attributepoints += 1
    print(
        "current attributes: strength "
        + str(character.strength)
        + ", dexterity "
        + str(character.dexterity)
        + ", constitution "
        + str(character.constitution)
        + ", intelligence "
        + str(character.intelligence)
        + ", wisdom "
        + str(character.wisdom)
        + ", charisma "
        + str(character.charisma)
    )

    while character.attributepoints > 0:
        s = input(
            "type an attribute (or leave blank to exit) to increase by 1: "
        )

        if s == "":
            break

        if character.attributes[resources.attributes.index(s)] < 20:
            character.attributes[resources.attributes.index(s)] += 1
            character.attributepoints -= 1
        else:
            print("attribute maxed; pick a different attribute")
            character.attributepoints += 1

    # update attributes from new list
    (
        character.strength,
        character.dexterity,
        character.constitution,
        character.intelligence,
        character.wisdom,
        character.charisma,
    ) = (x for x in character.attributes)

    # update character now in case int is increased enough to effect skillpoints
    character.update()

    # levelup skills
    character.skillpoints += 3 + character.intmod

    while character.skillpoints > 0:
        s = input("type a skill (or leave blank to exit) to increase by 1: ")

        if s == "":
            break
        # resources.skills is a copy of character.skills with strings instead of variables;
        # character.skills[resources.skills.index(s)] selects the appropriate skill via user input
        if s not in resources.skills:
            print("that is not a skill")

        # check to make sure the skill isn't maxed out
        elif character.skills[resources.skills.index(s)] < 5:
            # skills above 2 cost 2 to level instead of 1
            if character.skills[resources.skills.index(s)] > 2:
                if character.skillpoints > 1:
                    character.skills[resources.skills.index(s)] += 1
                    character.skillpoints -= 2
                else:
                    print("not enough to points level this skill")
            # base case: increment skill and decrement skillpoints
            else:
                character.skills[resources.skills.index(s)] += 1
                character.skillpoints -= 1
        else:
            print("skill maxed; pick a different skill")

    (
        character.acting,
        character.anthropology,
        character.xenoanthropology,
        character.diplomacy,
        character.medicine,
        character.vehicles,
        character.technology,
        character.xenotechnology,
        character.sleightofhand,
        character.stealth,
        character.insight,
        character.perception,
        character.survival,
        character.tactics,
        character.athletics,
        character.acrobatics,
    ) = (x for x in character.skills)

    # update character again
    character.update()


# TODO: create faction lists from factions dict, pass to savecharacters
def load():
    """builds factions, a dictionary of (name,list)s. don't use mid-session"""
    factions = {}

    for faction in os.listdir("./factions"):

        factions[faction] = []

        for character in os.listdir("./factions/" + faction):

            with open(
                "./factions/" + faction + "/" + character,
                "r",
                encoding="utf-8",
                errors="ignore",
            ) as file:

                characterjson = file.readline()
                factions[faction].append(jsonpickle.decode(characterjson))

    return factions


def savecharacters(characters):
    """characters is a list of character objects"""
    for character in characters:

        # characters must have a faction
        if character.faction == (None or ""):
            print(character.name + " has no faction, and wasn't saved.")

        # create directory if it doesn't exist
        elif not os.path.exists(".\\factions\\" + character.faction):
            os.makedirs(".\\factions\\" + character.faction)

        # create file if it doesn't exist
        Path(
            ".\\factions\\"
            + character.faction
            + "\\"
            + character.name
            + ".json"
        ).touch()

        # write
        f = open(
            ".\\factions\\"
            + character.faction
            + "\\"
            + character.name
            + ".json",
            "w",
            encoding="utf-8",
            errors="ignore",
        )
        f.write(jsonpickle.encode(character))
        f.close()


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

        while damage > 0:
            if defender.temphp > 0:
                defender.temphp -= 1
            else:
                defender.hp -= 1
            damage -= 1

        print(defender.name + " is at " + str(defender.hp) + " health.")

    else:
        print("miss!")
