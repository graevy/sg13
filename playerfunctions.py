import character
import resources
import item
from random import randint
from statistics import NormalDist


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


def initiative(character, dice=3, die=6):
    return character.initiative()


def printcontents(item):
    for thing in item.storage:
        print(item.name + ": " + thing.name)
        printcontents(thing)


def show(character):
    return character.show()


def update(character):
    """debug tool"""
    return character.update()


def equip(character, item, slot):
    """slot is a (camel)case-sensitive string"""

    if slot in resources.slots:
        if character.gear[resources.slots.index(slot)] == None:
            character.gear[resources.slots.index(slot)] = item

    (
        character.leftHand,
        character.rightHand,
        character.head,
        character.body,
        character.legs,
        character.belt,
        character.boots,
        character.gloves,
        character.back,
    ) = (x for x in character.gear)
    character.update()


def unequip(character, item, slot):
    """slot is a (camel)case-sensitive string"""

    # resources.slots is an identical slots list with strings instead of variables
    if slot in resources.slots:
        if character.gear[resources.slots.index(slot)] != None:
            character.inventory.append(
                character.gear[resources.slots.index(slot)]
            )
            character.gear[resources.slots.index(slot)] = None

    (
        character.leftHand,
        character.rightHand,
        character.head,
        character.body,
        character.legs,
        character.belt,
        character.boots,
        character.gloves,
        character.back,
    ) = (x for x in character.gear)
    character.update()


def grab(character, item, hand=None):

    if hand == None:
        if character.rightHand != None:
            character.rightHand = item
        elif character.leftHand != None:
            character.leftHand = item
        else:
            print("ope")

    if hand == "right":
        if character.rightHand != None:
            character.rightHand = item
        else:
            print("ope")

    if hand == "left":
        if character.leftHand != None:
            character.leftHand = item
        else:
            print("ope")

    character.update()


def stow(character, item, storageItem=None):
    if storageItem == None:
        character.inventory.append(item)
    else:
        storageItem.storage.append(item)


# TODO: testing
def odds(dc, dice=3, die=6):
    """return odds of succeeding a dice check"""
    # calculate mean, standard deviation, and then odds

    # calculate mean
    mean = (dice * die + die) / (2 * dice)

    # calculate standard deviation

    # discrete uniform variance formula
    dievariance = (die ** 2 - 1) / 12
    dicevariance = dievariance * dice
    stdev = dicevariance ** 0.5

    # calculate odds
    zscore = (dc - mean) / stdev
    odds = NormalDist(mu=mean, sigma=stdev).cdf(zscore)

    return odds

    # in python 2, (1 + erf(x/root2))/2 can be substituted for normaldist.cdf
