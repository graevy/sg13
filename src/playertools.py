import character
import item
from random import randint
from statistics import NormalDist
import rolls

def initiative(char):
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
        hand = 'left_hand'
    elif hand[:5].lower() == 'right':
        hand = 'right_hand'
    else:
        print("invalid hand slot")
    char.equip(item, slot=hand)

def stow(char, item, storageItem=None):
    char.stow(item, storageItem=storageItem)

def odds(dc, dice=rolls.dice, die=rolls.die):
    """return qualitative odds of succeeding a dice check

    Args:
        dc (int): to check
        dice (int, optional): number of dice. Defaults to rolls.dice.
        die (int, optional): number of sides per die. Defaults to rolls.die.

    Returns:
        str: a short string describing how likely a success is
    """
    # calculate odds
    odds = NormalDist(mu=rolls.dice_mean, sigma=rolls.dice_stdev).cdf(dc)
    percentSuccess = 100 - int(round(odds, 2) * 100)

    # in python 2, (1 + erf(x/root2))/2 can be substituted for normaldist.cdf

    if percentSuccess >= 50:
        if percentSuccess >= 80:
            if percentSuccess >= 95:
                return "almost certain"
            return "very likely"
        return "probable"
    elif percentSuccess < 20:
        if percentSuccess < 5:
            return "remote"
        return "unlikely"
    return "possible"
