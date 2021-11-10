import character
import item
import random
from statistics import NormalDist
from copy import deepcopy
import json
import os
import rolls

sep = os.sep


def create(mode=0, **kwargs):
    """Character creation function

    Args:
        mode (int, optional): level of detail. Defaults to 0.
        kwargs (dict, optional): to include on creation. Defaults to {}.
    """
    with open(f".{sep}races{sep}{kwargs.get('race','human')}{sep}{kwargs.get('race','human')}.json") as f:
        defaults = json.load(f)

    # TODO P2: this doesn't handle invalid races/classes properly because 
    # dict membership checking happens in the character constructor. it
    # only checks invalid typing. if this ends up front-facing it needs an enum.
    # this defaults_dict implementation is pretty hamfisted
    def handle_input(key, defaults_dict=defaults):
        # infinite loop allows restarting loop iterations
        while True:
            try:
                value = input(f'{key} <<< ')
                # blank input uses the default value
                if value == '':
                    return defaults_dict[key]
                # must dynamically type cast input string before returning
                return type(defaults_dict[key])(value)
            except ValueError:
                print(f" invalid entry for {key}")

    data = {} # this gets populated and then returned
    basics = ['name', 'race', 'clas', 'faction', 'level']

    # stuffing the basic values into data
    for basic in basics:
        if basic not in kwargs:
            data[basic] = handle_input(basic)

    # optionally manually edit character attributes and skills
    if mode:
        attrs = defaults['attributes']
        data['attributes'] = {attr_name:handle_input(attr_name,attrs) \
            if attr_name not in kwargs else None for attr_name in attrs}
        skills = defaults['skills']
        data['skills'] = {skill_name:handle_input(skill_name,skills) \
            if skill_name not in kwargs else None for skill_name in skills}
        
        # gear editing
        if mode > 1:
            slots = defaults['slots']
            data['slots'] = {slot_name:handle_input(slot_name,slots) \
                if slot_name not in kwargs else None for slot_name in slots}

    # at the end, insert kwargs, overwriting any Nones
    data = data | kwargs

    # this permits create(strength=15) instead of create(attributes={strength:15,dexterity:10...})
    # pop also neatly cleans the data dict before assignment if, uh, anyone were to include that error
    for key in kwargs:
        if key in defaults['attributes']:
            data['attributes'][key] = data.pop(key)
        if key in defaults['skills']:
            data['skills'][key] = data.pop(key)

    return character.Character.new(**data)


# TODO P3: expanded 5e longrest implementation
def long_rest(*character_lists):
    """pass lists of character objects to reset their hp"""
    for character_list in character_lists:
        for character in character_list:
            character.heal()

def group_initiative(*character_lists, print_output=True):
    """generates initiative rolls from lists of characters.

    Returns:
        list: of character objects sorted by an initiative roll
    """
    out = sorted((character for character_list in character_lists for character in character_list),
        key=lambda character: character.initiative(), reverse=True)

    if print_output:
        for character in out:
            print(character)
    else:
        return out


def set_dc(success_odds, round_down=True):
    """returns the DC of a % success chance

    Args:
        success_odds (int): the 0-99 chance of action success.
        round_down (bool, optional): floors the DC -- for lower variance rolls. Defaults to True.

    Returns:
        int: the corresponding DC
    """
    success_odds /= 100

    # calculate a DC using the inverse cumulative distribution function
    dc = NormalDist(mu=rolls.dice_mean, sigma=rolls.dice_stdev).inv_cdf(success_odds)

    # rotate around the 10.5 mean (17 becomes 4, 11 becomes 10, etc)
    # alternatively: dc = dice*(die+1) - dc
    dc = -(dc - rolls.dice_mean) + rolls.dice_mean

    if round_down:
        # casting floats to ints truncates in python. don't have to import math
        return f"{int(dc)} (rounded down from {dc})"
    return f"{round(dc)} (rounded from {dc})"

def odds_num(dc):
    """return odds of succeeding a dice check

    Args:
        dc (int): Dice check to pass/fail

    Returns:
        [str]: Percent chance of success
    """
    odds = NormalDist(mu=rolls.dice_mean, sigma=rolls.dice_stdev).cdf(dc)
    percent_success = 100 - int(round(odds, 2) * 100)

    return f"DC of {dc} rolling {dice}d{die}: {percent_success}% success"
    # in python 2, (1 + erf(x/root2))/2 can be substituted for normaldist.cdf

# alias commands
def hurt(char, amount):
    char.hurt(amount)

def heal(char, amount=None):
    if amount is None:
        char.heal()
    else:
        char.heal(amount)

def level_up(char):
    char.level_up()


def dismember(char, at_most=2):
    """permanently randomly decrease a character's attribute

    Args:
        char (character Obj): to dismember
        at_most (int, optional): maximum possible value to decrease by. Defaults to 2.
    """
    tuple(char.attributes.values())[random.randrange(0,len(char.attributes))] -= random.randint(1,at_most)
    char.update()

def random_names(n, *namefiles):
    """spits out random names from namefiles

    Args:
        n (int): number of random names to return
        *namefiles (strings): of file locations. 2 namefiles produces e.g. 'john smith', 1 yields 'john'

    Returns:
        tuple: of ('random name' 'for each' 'namefile used') strings
    """
    # i grabbed (and improved via enumerate! see EOF) the beautiful spaceless unknown-file-length access-random-element
    # algorithm from the python cookbook expecting it to be faster. random.uniform takes about 200ns
    # and append takes about 50ns; this space-hog is faster

    # build a list of lists of all names from each file
    namefile_list_list = []
    for namefile in namefiles:
        namefile_list = []
        with open(namefile, encoding='utf-8') as f:
            for line in f:
                namefile_list.append(line) # name whitespace and trailing newline preserved
        namefile_list_list.append(namefile_list) # better to rstrip on assignment

    # now actually create and return the random names
    return [' '.join(
        random.choice(namefile_list).rstrip() for namefile_list in namefile_list_list
        ) for henchman in range(n)]

    # fun golf if you don't mind not closing files
    # return [' '.join(
    #     random.choice(namefile_list).rstrip() for namefile_list in [[line for line in open(namefile)] for namefile in namefiles]
    #     ) for henchman in range(n)]


def henchmen(n, *namefiles, attributes=None, faction=None):
    """generates henchmen for use in combat encounters

    Args:
        n (int): number of henchmen
        namefiles (str, optional): text filenames to source random character names from
        attributes (dict, optional): a data dict containing elements for character construction
        faction (list, optional): a faction list to put henchmen inside

    Returns:
        (list): faction list, containing all the henchmen
    """
    # did you know mutable default args are only instantiated when a function is defined? that was a fun session
    if attributes is None:
        attributes = {}
    if faction is None:
        faction = []

    # use human as a default race for sourcing names
    if not namefiles:
        namefiles = os.listdir(f".{sep}races{sep}{attributes.get('race','human')}{sep}names")
    # if the race wasn't given any namefiles, use human names. this gets very entertaining
    if not namefiles:
        namefiles = os.listdir(f".{sep}races{sep}human{sep}names")
    # generate random names
    names = random_names(n, *namefiles)

    # add a list of characters to the supplied list (if any), randomly name them from the names list, and return it
    return faction + [character.Character.new(   **(attributes | {'name':names.pop()})   ) for x in range(n)]

# TODO P3: this is doubling as a factory method and that probably shouldn't happen
def load_item(item_to_load):
    """(recursively) loads an item in memory

    Args:
        item (dict or str): an attr dict to manually create an item with, or a filename str to load from

    Returns:
        Item: loaded
    """
    if isinstance(item_to_load, dict):
        item_json = item_to_load
    elif isinstance(item_to_load, str):
        with open(f'.{sep}items{sep}{item_to_load}.json') as f:
            item_json = json.load(f)

    # ladder to determine item type to construct
    # this order actually matters a lot, because some weapons have bonus_ac
    if 'range' in item_json:
        item_obj = item.Weapon(**item_json)
    elif 'bonus_ac' in item_json:
        item_obj = item.Armor(**item_json)
    else:
        item_obj = item.Item(**item_json)

    item_obj.storage = [load_item(stored_item) for stored_item in item_obj.storage]
    return item_obj

# this is the 5th iteration of the load function. it works well, but it's just convoluted.
# i think the object creation could be smoother. it could use something simpler than os.walk, probably os.listdir.
# os.walk's python list is the wrong data structure here. a linked list makes the most sense.
# a deque import is costly but scales well. realistically this doesn't matter
def load():
    """builds factions, a nested dict eventually containing lists of character Objs.
    """

    # TODO P3: this broke
    if 'factions' in globals():
        raise Exception("load() attempted to overwrite factions")

    # recursive function to both load characters (with items) and populate the root factions dict
    def populate_factions(root_list, cd, files):
        # root_list is from walker e.g. ['sg13', 'sgc']. cd is the current dictionary
        outer_dict = root_list.pop() # sgc will equal {'sg13':_, ...} so it's "outer"

        # base case: root_list is empty after being popped; now dict can be populated
        if not root_list:
            faction = []
            for file_str in files:
                with open(file_str) as f:
                    # convert each serialized character into an object,
                    char_obj = character.Character(**json.load(f))
                    # convert each serialized item into an object (load_item does recursion),
                    char_obj.slots = {slot:load_item(item) if item else None \
                        for slot,item in char_obj.slots.items()}
                    # add the character to the faction,
                    faction.append(char_obj)
            # send faction to dict
            cd[outer_dict] = faction
            return

        # otherwise, keep traversing
        if outer_dict not in cd:
            cd[outer_dict] = {}
        populate_factions(root_list=root_list, cd=cd[outer_dict], files=files)

    # generator yielding file locations
    #                               root:           dirs       files
    # walker output looks like ['./factions'], ['sgc','trust'], []
    walker = ((root, dirs, files) for root,dirs,files in os.walk(f".{sep}factions"))

    # first yield is sort of like a dir head (it has no root), so it gets its own statement
    factions = {key:{} for key in next(walker)[1]} # factions is currently e.g. {'sgc':{}, 'trust':{}}

    #    (dirs unused)
    for root, _, files in walker:
        if files:
            files = [root+sep+file_str for file_str in files]

            # root.split(sep) looks like [".", "factions", "<faction1>", "<faction2>", ...]
            # [::-1] reverses the list; populate_factions can root_list.pop() efficiently
            # [:1:-1] slices out the first 2 (junk) elements from the original unreversed list
            populate_factions(root_list=root.split(sep)[:1:-1], cd=factions, files=files)

    return factions


def save(iterable: dict, path=f'.{sep}factions{sep}'):
    """writes all character data to local jsons

    Args:
        iterable (dict): arbitrarily nested dicts eventually containing lists of character objects
        path (str): the directory to save character files in
    """

    # put every nested dict on the stack
    if isinstance(iterable, dict):
        for key, value in iterable.items(): # e.g. path="./factions/sgc/" first
            save(value, path=(path+key+sep))

    # encountered a char_obj list
    if isinstance(iterable, list):
        for char_obj in iterable:
            # save a copy of the character, so the session can continue if needed
            char_copy = deepcopy(char_obj)
            # create directories if they don't exist
            if not os.path.exists(path):
                os.makedirs(path)

            # character faction should be updated on each save
            # it is purely cosmetic at this point, though
            # this slicing ultimately does ".\\factions\\x/y/z/" -> "x/y/z"
            char_copy.faction = sep.join(path.split(sep)[2:-1]).replace('\\','/') # for windows

            # write character to file
            with open(f'{path}{char_copy.name}.json', 'w+', encoding='utf-8') as f:
                json.dump(char_copy.get_json(), f)


def get_chars(char_dict, out_list=None):
    """recursively get character objects from lists inside a nested dict

    Args:
        char_dict (dict): of dicts [...] of lists of char_objs

    Returns:
        list: of char_objs
    """
    if out_list is None: # thanks guido
        out_list = []
    for value in char_dict.values():
        if isinstance(value,dict):
            get_chars(value,out_list)
        else:
            out_list += value
    return out_list

# from my original 2019 codebase
# i've improved a lot since then. i gave it a facelift, but
# it's a lot less readable. it works, so i'm not touching it
def attack(attacker, defender, weapon=None, distance=0, cover=0):
    """attacker rolls against defender with weapon from distance

    Args:
        attacker (Character): Character attacking
        defender (Character): Character defending
        weapon (Weapon): Attacker's weapon. Defaults to None.
        distance (int, optional): Attack distance. Defaults to 0.
        cover (int, optional): % defender is covered. Defaults to None.
    """
    # factoring distance
    if distance == 0:
        distanceMod = 1
    else:
        # 2 is arbitrary
        distanceMod = 1 - (distance / weapon.range) ** 2
        if distanceMod < 0:
            distanceMod = 0

    # factoring cover
    if cover == 0:
        coverMod = 0
    else:
        coverMod = int(cover // 25)

    # fetch weapon
    if weapon is None:
        if attacker.slots['right_hand'] is None:
            if attacker.slots['left_hand'] is None:
                return "no valid attacker wep" # TODO: unarmed combat
            else:
                weapon = attacker.slots['left_hand']
        else:
            weapon = attacker.slots['right_hand']

    # weapon mods to hit
    mod = 0
    if weapon.proficiency == "strength":
        mod = attacker.self.bonus_attrs['strength']
    elif weapon.proficiency == "dexterity":
        mod = attacker.self.bonus_attrs['dexterity']
    elif weapon.proficiency == "finesse":
        mod = max(attacker.self.bonus_attrs['strength'], attacker.self.bonus_attrs['dexterity'])

    # hit calculation
    hitcalc = roll3d6() + mod

    # dual wield penalty
    if attacker.slots['left_hand'] is not None and attacker.slots['right_hand'] is not None:
        hitcalc -= 2

    # qc penalty for long range weapons
    if weapon.cqc_penalty > 0 and distance > 3:
        hitcalc -= 2 * weapon.cqc_penalty
        print("close combat weapon penalty applied")

    # does the attack hit?
    if hitcalc > (defender.AC + coverMod):
        # damage calculation
        damage = (
            round(
                rolls.roll(2, weapon.damage // 2) * distanceMod
            )
        )

        print(f"{attacker.name} rolled {hitcalc} to hit {defender.name} for {damage}")

        defender.hurt(totalDamage=damage)

        print(f"{defender.name} is at {defender.hp} health")

    else:
        print("miss!")



# this is what i wrote for the spaceless variant. this is only useful for namefiles that exceed system memory. oh well

# names = []
# for x in range(n):
#     name = ''
#     for namefile in namefiles:
#         selected_line = None
#         with open(namefile) as f:
#             for idx,line in enumerate(f):
#                 if random.uniform(0,idx) < 1:
#                     selected_line = line
#         name += selected_line.rstrip() + ' '
#     names.append(name.rstrip())
# return names


# some golf experiments i'm leaving here
# def getChars2(charDict, outList=[])
#     [getChars2(value, outList) if isinstance(value,dict) else outList.extend(value) for value in iterable.values()]
#     return outList

# def getChars3(charDict):
#     # this is pretty fast, but puts out nested lists
#     return [value if isinstance(value,list) else getChars3(value) if isinstance(value,dict) else value for value in charDict.values()]
