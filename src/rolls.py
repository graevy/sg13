
import json
import random

with open('./cfg/diceconfig.json') as f:
    diceConfig = json.load(f)
dice = diceConfig['dice'] # number of dice used in each roll
die  = diceConfig['die']  # number of sides per die

# calculate mean. dice*die is max, dice is min, dice*(die+1) is max+min
diceMean = (dice * (die + 1)) / 2
# calculate standard deviation via discrete uniform variance formula:
# (n^2 - 1) / 12
diceStDev = dice * ((die**2 - 1) / 12)

def newDice(newDice, newDie):
    """changes system default dice settings

    Args:
        newDice (int): of dice per roll
        newDie (int): of sides per die
    """
    global dice,die
    dice = newDice
    die = newDie
    diceConfig = {'dice':dice, 'die':die}
    with open('./cfg/diceconfig.json', 'w+') as f:
        json.dump(diceConfig, f)

def roll(dice=dice, die=die):
    """custom roll, takes (dice)d(die)"""
    return sum(random.randint(1, die) for x in range(dice))

def d20():
    """it's a d20. what do you want from me"""
    return random.randint(1, 20)

def mid3d20():
    """mid variance standard roll"""
    return sorted([d20() for x in range(3)])[1]

# don't look too closely
def IIId6():
    """low variance standard roll"""
    return roll(3, 6)

def VIId2():
    """lowest variance standard roll"""
    return roll(7, 2)

def disadvantage(dice=dice, die=die):
    """rolls disadvantage for (dice)d(die)"""
    return min(roll(dice, die), roll(dice, die))

def advantage(dice=dice, die=die):
    """rolls advantage for (dice)d(die)"""
    return max(roll(dice, die), roll(dice, die))

def initiative(char):
    return char.initiative()
