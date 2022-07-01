import random
from cfg.cfg import cfg
CFG = cfg.configs

dice = CFG.DICE # number of dice used in each roll
die  = CFG.DIE  # number of sides per die

# calculate mean. dice*die is max, dice is min, dice*(die+1) is max+min
dice_mean = (dice * (die + 1)) / 2
# calculate standard deviation via discrete uniform variance formula:
# (n^2 - 1) / 12
dice_stdev = dice * ((die**2 - 1) / 12)

# def new_dice(new_dice, new_die):
#     """changes system default dice settings

#     Args:
#         new_dice (int): of dice per roll
#         new_die (int): of sides per die
#     """
#     global dice,die
#     dice = new_dice
#     die = new_die
#     dice_config = {'dice':dice, 'die':die}
#     with open(CFG.DICE_CONFIG_DIR, 'w+', encoding='utf-8') as f:
#         json.dump(dice_config, f)

# recommend 1d20, 3d6, 7d2 for more -> less variance
def roll(dice=dice, die=die):
    """custom roll, takes (dice)d(die)"""
    return sum(random.randint(1, die) for x in range(dice))

def d20():
    """it's a d20. what do you want from me"""
    return random.randint(1, 20)

def mid3d20():
    """mid variance standard roll"""
    return sorted(d20() for x in range(3))[1]

def disadvantage(dice=dice, die=die):
    """rolls disadvantage for (dice)d(die)"""
    return min(roll(dice, die), roll(dice, die))

def advantage(dice=dice, die=die):
    """rolls advantage for (dice)d(die)"""
    return max(roll(dice, die), roll(dice, die))
