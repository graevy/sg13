import random
from statistics import NormalDist
from copy import deepcopy
import json
import os

import character
import item
import rolls
import cfg.dirs

SEP = os.sep

def create_character_manual(mode=0, **kwargs):
    """Stepwise character creation function

    Args:
        mode (int, optional): level of detail. Defaults to 0.
        kwargs (dict, optional): to include on creation. Defaults to {}.
    """
    with open(RACES_DIR + kwargs.get('race','human') + SEP + 'defaults.json') as f:
        defaults = json.load(f)

    # TODO P2: this doesn't handle invalid races/classes properly because 
    # dict membership checking happens in the character constructor. it
    # only checks invalid typing. if this ends up front-facing it needs an enum.
    # this defaults_dict implementation is pretty hamfisted
    def handle_input(key, defaults_dict=defaults):
        # infinite loop allows restarting loop iterations
        # this could be a recursive function but i'm worried about unbounded stack frames with user input
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

    attrs = {} # this gets populated and then returned
    basics = ['name', 'race', 'class_', 'faction', 'level']

    # stuffing the basic values into attrs
    for basic in basics:
        if basic not in kwargs:
            attrs[basic] = handle_input(basic)

    # optionally manually edit character attributes and skills
    if mode:
        attrs = defaults['attributes']
        attrs['attributes'] = {attr_name:handle_input(attr_name,attrs) \
            if attr_name not in kwargs else None for attr_name in attrs}
        skills = defaults['skills']
        attrs['skills'] = {skill_name:handle_input(skill_name,skills) \
            if skill_name not in kwargs else None for skill_name in skills}
        
        # gear editing
        if mode > 1:
            slots = defaults['slots']
            attrs['slots'] = {slot_name:handle_input(slot_name,slots) \
                if slot_name not in kwargs else None for slot_name in slots}

    # at the end, insert kwargs, overwriting any Nones
    attrs = attrs | kwargs

    # this permits create(strength=15) instead of create(attributes={strength:15,dexterity:10...})
    # pop also neatly cleans the attrs dict before assignment if, uh, anyone were to include that error
    for key in kwargs:
        if key in defaults['attributes']:
            attrs['attributes'][key] = attrs.pop(key)
        if key in defaults['skills']:
            attrs['skills'][key] = attrs.pop(key)

    return character.Character.create(attrs)

def create_item_manual(mode=0, **kwargs):
    # TODO: P2
    pass

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

def random_names(n, name_files, name_separator=' '):
    """spits out random names from name_files

    Args:
        n (int): number of random names to return
        name_files (iterable): containing files e.g. ["./races/human/names/firstnames.txt"]
        name_separator (str): to put between names

    Returns:
        tuple: of ('random name' 'for each' 'namefile used') strings
    """

    # build a list of lists of all names from each file
    name_file_list_list = []
    for name_file in name_files:
        name_file_list = []
        with open(name_file, encoding='utf-8') as f:
            for line in f:
                name_file_list.append(line) # name whitespace and trailing newline preserved
        name_file_list_list.append(name_file_list) # better to rstrip on assignment

    # now actually create and return the random names
    return [name_separator.join(
        random.choice(name_file_list).rstrip() for name_file_list in name_file_list_list
        ) for _ in range(n)]


def henchmen(n, template=None, attributes=None, faction=None):
    """generates henchmen for use in combat encounters

    Args:
        n (int): number of henchmen
        template (str, optional): the name (no extension) of a pre-generated character file e.g. 'airman'
        attributes (dict, optional): containing elements for character construction
        faction (list, optional): to extend with the generated henchmen inside

    Returns:
        (list): containing all the henchmen
    """
    # mutable default args are only instantiated when a function is defined, not called
    if attributes is None:
        attributes = {}
    if faction is None:
        faction = []

    # using a template means we source names from its race
    if template:
        with open(cfg.dirs.TEMPLATES_DIR + template + '.json', encoding='utf-8') as f:
            attributes = json.load(f) | attributes
        race = attributes['race']
    elif 'race' in attributes and os.listdir(RACES_DIR + attributes['race'] + SEP + "names"):
        race = attributes['race']
    else:
        race = 'human'

    race_path = cfg.dirs.RACES_DIR + race + SEP + 'names'
    name_files = [race_path + SEP + name_file for name_file in os.listdir(race_path)]
    names = random_names(n, name_files)

    # add a list of characters to the supplied list (if any), randomly name them from the names list, and return it
    return faction + [character.Character.create(attributes | {'name':names.pop()}) for _ in range(n)]

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
        with open(cfg.dirs.ITEMS_DIR + item_to_load + '.json') as f:
            item_json = json.load(f)

    # ladder to determine item type to construct
    # this order actually matters a lot, because some weapons have bonus_ac
    if 'range' in item_json:
        item_obj = item.Weapon(item_json)
    elif 'bonus_ac' in item_json:
        item_obj = item.Armor(item_json)
    else:
        item_obj = item.Item(item_json)

    item_obj.storage = [load_item(stored_item) for stored_item in item_obj.storage]
    return item_obj

# this is the 5th iteration of the load function. it works well, but it's just convoluted.
# i think the object creation could be smoother. it could use something simpler than os.walk, probably os.listdir.
# os.walk's python list is the wrong data structure here. a linked list makes the most sense.
# a deque import is costly but scales well. realistically this doesn't matter
def load():
    """builds factions, a nested dict eventually containing lists of character Objs.
    """

    # TODO P3: this broke because it got moved inside this translation unit
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
                    char_obj = character.Character(json.load(f))
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
    walker = ((root, dirs, files) for root,dirs,files in os.walk(cfg.dirs.FACTIONS_DIR))

    # first yield is sort of like a dir head (it has no root), so it gets its own statement
    factions = {key:{} for key in next(walker)[1]} # factions is currently e.g. {'sgc':{}, 'trust':{}}

    for root, _, files in walker:
        if files:
            files = [root + SEP + file_str for file_str in files]

            # root.split(SEP) looks like [".", "factions", "<faction1>", "<faction2>", ...]
            # [:1:-1] slices out the first 2 (junk) elements from the original unreversed list,
            # then reverses the list so populate_factions can root_list.pop() efficiently.
            populate_factions(root_list=root.split(SEP)[:1:-1], cd=factions, files=files)

    return factions


def save(iterable, path=cfg.dirs.FACTIONS_DIR):
    """writes all character data to local jsons

    Args:
        iterable (dict): arbitrarily nested dicts eventually containing lists of character objects
        path (str): the directory to save character files in
    """

    # put every nested dict on the stack
    if isinstance(iterable, dict):
        for key, value in iterable.items(): # e.g. path="./factions/sgc/" first
            save(value, path=(path+key+SEP))

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
            char_copy.faction = SEP.join(path.split(SEP)[2:-1]).replace('\\','/') # replace is for windows

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


# this is what i wrote for the spaceless variant. this is only useful for namefiles that exceed system memory. oh well
# it's almost 20% faster than the algorithm in the python cookbook! mostly achieved with enumerate.

# names = []
# for x in range(n):
#     name = ''
#     for namefile in namefiles:
#         with open(namefile) as f:
#             for idx,line in enumerate(f, start=1):
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
