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
    return sorted([roll() for x in range(3)])[1]


def roll3d6():
    """low variance standard roll"""
    return roll(6, 3)


def roll7d2():
    """lowest variance standard roll"""
    return roll(7, 2)


def disadvantage(dice=1, die=20):
    """rolls disadvantage for (dice)d(die)"""
    return min(roll(dice, die), roll(dice, die))


def advantage(dice=1, die=20):
    """rolls advantage for (dice)d(die)"""
    return max(roll(dice, die), roll(dice, die))


def initiative(char, dice=3, die=6):
    return char.initiative()


def printContents(item):
    for thing in item.storage:
        print(item.name + ": " + thing.name)
        printContents(thing)


def show(char):
    return char.show()


def update(char):
    """debug tool"""
    return char.update()


def equip(char, item, slot):
    """slot is a string"""
    char.equip(item, slot)


def unequip(char, item, slot):
    """slot is a string"""
    char.unequip(item, slot)


def grab(char, item, hand=None):
    if hand[:3].lower() == 'left':
        hand = 'leftHand'
    elif hand[:3].lower() == 'right':
        hand = 'rightHand'
    else:
        print("invalid hand slot")
    char.equip(item, slot=hand)


def stow(char, item, storageItem=None):
    char.stow(item, storageItem=storageItem)


# TODO: return quantative vs qualitative values depending on mode parameter
def odds(dc, dice=3, die=6):
    """return odds of succeeding a dice check

    Args:
        dc (int): Dice check to pass/fail
        dice (int, optional): Number of dice. Defaults to 3.
        die (int, optional): Number of sides per die. Defaults to 6.

    Returns:
        [str]: Percent chance of success
    """
    # calculate mean, standard deviation, and then odds

    # calculate mean. dice*die is max, dice is min, dice*(die+1) is max+min
    mean = (dice * (die + 1)) / 2

    # calculate standard deviation via discrete uniform variance formula:
    # (n^2 - 1) / 12
    dievariance = (die ** 2 - 1) / 12
    dicevariance = dievariance * dice
    stdev = dicevariance ** 0.5

    # calculate odds
    odds = NormalDist(mu=mean, sigma=stdev).cdf(dc)
    percentSuccess = 100 - int(round(odds, 2) * 100)

    return (str(percentSuccess) + '%')

    # in python 2, (1 + erf(x/root2))/2 can be substituted for normaldist.cdf
