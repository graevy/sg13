import character
import item
from random import randint
from statistics import NormalDist
import rolls

def initiative(char, dice=3, die=6):
    return char.initiative()


def printContents(item):
    for thing in item.storage:
        print(f"{item.name}: {thing.name}")
        printContents(thing)


def show(char):
    return char.show()


def update(char):
    """debug tool"""
    char.update()


def equip(char, item, slot):
    """slot is a string"""
    char.equip(item, slot)
    char.update()


def unequip(char, item, slot):
    """slot is a string"""
    char.unequip(item, slot)
    char.update()


def grab(char, item, hand=None):
    if hand[:4].lower() == 'left':
        hand = 'leftHand'
    elif hand[:5].lower() == 'right':
        hand = 'rightHand'
    else:
        print("invalid hand slot")
    char.equip(item, slot=hand)


def stow(char, item, storageItem=None):
    char.stow(item, storageItem=storageItem)


def oddsNum(dc, dice=3, die=6):
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
    dieVariance = (die ** 2 - 1) / 12
    diceVariance = dieVariance * dice
    stDev = diceVariance ** 0.5

    # calculate odds
    odds = NormalDist(mu=mean, sigma=stDev).cdf(dc)
    percentSuccess = 100 - int(round(odds, 2) * 100)

    return f"{percentSuccess}%"
    # in python 2, (1 + erf(x/root2))/2 can be substituted for normaldist.cdf

def odds(dc, dice=3, die=6):
    n = int(oddsNum(dc, dice, die)[:-1])

    if n >= 50:
        if n >= 80:
            if n >= 95:
                return "almost certain"
            return "very likely"
        return "probable"
    elif n < 20:
        if n < 5:
            return "remote"
        return "unlikely"
    return "possible"
