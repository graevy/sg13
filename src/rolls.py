#Just import this instead of boiler plating these into every file.

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
