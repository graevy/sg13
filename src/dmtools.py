import character
import item
import random
from statistics import NormalDist
from copy import deepcopy
import json
import os
import rolls

sep = os.sep

# muuuch better than previous. now with easy default value input and extensible modes
def create(mode=0, **kwargs):
    """Character creation function

    Args:
        mode (int, optional): level of detail. Defaults to 0.
        kwargs (dict, optional): to include on creation. Defaults to {}.
    """
    def handle_input(key, defaults_dict=character.defaults):
        # TODO P2: this doesn't handle invalid races/classes properly because 
        # dict membership checking happens in the character constructor. it
        # only checks invalid typing. if this ends up front-facing it needs a
        # valids dict to check input against valid ranges or something
        while True:
            try:
                value = input(f'{key} <<< ')
                # blank input uses the character.default value
                if value == '':
                    return defaults_dict[key]
                # must dynamically type cast input string before returning
                return type(defaults_dict[key])(value)
            except ValueError:
                print(f" invalid entry")

    data = {} # this gets populated and then returned
    basics = ['name', 'race', 'clas', 'faction', 'level']

    # stuffing the basic values into data
    for basic in basics:
        if basic not in kwargs:
            data[basic] = handle_input(basic)

    # optionally manually edit character attributes and skills
    if mode:
        attrs = character.defaults['attributes']
        data['attributes'] = {attr_name:handle_input(attr_name,attrs) \
            if attr_name not in kwargs else None for attr_name in attrs}
        skills = character.defaults['skills']
        data['skills'] = {skill_name:handle_input(skill_name,skills) \
            if skill_name not in kwargs else None for skill_name in skills}
        
        # gear editing
        if mode > 1:
            slots = character.defaults['slots']
            data['slots'] = {slot_name:handle_input(slot_name,slots) \
                if slot_name not in kwargs else None for slot_name in slots}

    # at the end, insert kwargs, overwriting any Nones
    data = data | kwargs

    # this permits create(strength=15) instead of create(attributes={strength:15,dexterity:10...})
    # pop also neatly cleans the data dict before assignment if, uh, anyone includes that error
    for key in kwargs:
        if key in character.defaults['attributes']:
            data['attributes'][key] = data.pop(key)
        if key in character.defaults['skills']:
            data['skills'][key] = data.pop(key)

    return character.Character.new(**data)


# TODO P3: expanded 5e longrest implementation
def longrest(*character_lists):
    """pass lists of character objects to reset their hp"""
    for character_list in character_lists:
        for character in character_list:
            character.heal()


def groupInitiative(*character_lists):
    """generates initiative rolls from lists of characters.

    Returns:
        list: of (initiative roll, character name) tuples
    """
    return sorted(
        [(character.initiative(), character.name) for character_list in character_lists for character in character_list]
    , reverse=True)

def skillCheck(char_obj, stat, dc, rollFn=rolls.IIId6):
    return True if rollFn() + char_obj.skills[stat] + char_obj.bonus_skills[stat] >= dc else False

def setDc(success_odds, dice=rolls.dice, die=rolls.die, roundDown=True):
    """returns the DC of a % success chance

    Args:
        success_odds (int): the 0-99 chance of action success.
        dice (int, optional): number of dice to roll. Defaults to rolls.dice.
        die (int, optional): faces per die. Defaults to rolls.die.
        roundDown (bool, optional): floors the DC -- for lower variance rolls. Defaults to True.

    Returns:
        int: the corresponding DC
    """
    success_odds /= 100

    # calculate a DC using the inverse cumulative distribution function
    dc = NormalDist(mu=rolls.dice_mean, sigma=rolls.dice_stdev).inv_cdf(success_odds)

    # rotate around the 10.5 mean (17 becomes 4, 11 becomes 10, etc)
    # alternatively: dc = dice*(die+1) - dc
    dc = -(dc - rolls.dice_mean) + rolls.dice_mean

    if roundDown:
        # casting floats to ints truncates in python. don't have to import math
        return f"{int(dc)} (rounded down from {dc})"
    return f"{round(dc)} (rounded from {dc})"

def oddsNum(dc, dice=rolls.dice, die=rolls.die):
    """return odds of succeeding a dice check

    Args:
        dc (int): Dice check to pass/fail
        dice (int, optional): Number of dice. Defaults to 3.
        die (int, optional): Number of sides per die. Defaults to 6.

    Returns:
        [str]: Percent chance of success
    """
    odds = NormalDist(mu=rolls.dice_mean, sigma=rolls.dice_stdev).cdf(dc)
    percentSuccess = 100 - int(round(odds, 2) * 100)

    return f"DC of {dc} rolling {dice}d{die}: {percentSuccess}% success"
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


def dismember(char, atMost=2):
    """permanently randomly decrease a character's attribute

    Args:
        char (character Obj): to dismember
        atMost (int, optional): maximum possible value to decrease by. Defaults to 2.
    """
    list(char.attributes.values())[random.randrange(0,len(char.attributes))] -= random.randint(1,atMost)
    char.update()

def random_names(n, *namefiles, threshold=3):
    """spits out random names from namefiles

    Args:
        n (int): number of random names to return
        *namefiles (strings): e.g. 2 namefiles produces 'john smith', 1 yields 'john'
        threshold (int, optional): above threshold, switches to O(n) space algorithm. Defaults to 2.

    Returns:
        tuple: of ('random name' 'for each' 'namefile used') strings
    """

    # use a faster space-less algorithm (crediting Python Cookbook) if fewer names are needed
    if n <= threshold:
        names = ['' for x in range(n)]
        for idx,_ in enumerate(names):
            for namefile in namefiles:
                line_index = 0
                selected_line = None
                with open(namefile, 'r') as f:
                    while True:
                        line = f.readline()
                        if not line: # readline() returns '' at EOF
                            break
                        line_index += 1
                        # first line has a 1/1 chance of being selected
                        # the nth line has a 1/n chance of overwriting previous selection
                        if random.uniform(0, line_index) < 1:
                            selected_line = line

                # (add spaces between firstname nthname lastname)
                names[idx] += selected_line.rstrip() + ' '
            names[idx].rstrip() # remove trailing space
        return names

    # otherwise, store all file data in lists for faster accesses
    else:
        # build a list of lists of random names from each file
        namefile_list_list = []
        for namefile in namefiles:
            namefile_list = []
            with open(namefile, 'r') as f:
                for line in f:
                    namefile_list.append(line) # name whitespace and trailing newline preserved
            namefile_list_list.append(namefile_list) # better to rstrip on assignment

        # now actually create and return the random names
        return tuple((' '.join(
            random.choice(namefile_list).rstrip() for namefile_list in namefile_list_list
            ) for henchman in range(n)))


def henchmen(n, *namefiles, attributes={}, faction=[]):
    """generates henchmen for use in combat encounters

    Args:
        n (int): number of henchmen
        namefiles (str, optional): text filenames to source random character names from
        attributes (dict, optional): a data dict containing elements for character construction
        faction (list, optional): a faction list to put henchmen inside

    Returns:
        (list): faction list, containing all the henchmen
    """
    # a "def foo(*args=(args,here)):" syntax is needed
    if not namefiles:
        namefiles = tuple(('firstnames.txt','lastnames.txt'))

    # create list of henchmen,
    characters = [character.Character.new(**attributes) for x in range(n)]
    # generate random names,
    names = random_names(n, *namefiles)
    # name the characters
    for idx in range(n):
        characters[idx].name = names[idx]
    # add them to the faction,
    faction += characters
    # send it
    return faction

# TODO P3: this thing is doubling as a factory method and that probably shouldn't happen
def load_item(item_attrs):
    """(recursively) loads an item in memory

    Args:
        item_attrs (dict or str): an attr dict to manually create an item with, or a filename str to load from

    Returns:
        Item: loaded
    """
    if type(item_attrs) == dict:
        item_json = item_attrs
    elif type(item_attrs) == str:
        with open(f'.{sep}items{sep}'+item_attrs) as f:
            item_json = json.load(f)

    # ladder to determine item type to construct
    # this order actually matters a lot, because some weapons have bonus_ac
    if 'range' in item_json:
        item_obj = item.Weapon(**item_json)
    elif 'bonus_ac' in item_json:
        item_obj = item.Armor(**item_json)
    else:
        item_obj = item.Item(**item_json)

    item_obj.storage = [load_item(item) for item in item_obj.storage]
    return item_obj

# os.walk's python list is the wrong data structure here. a linked list makes the most sense, I think.
# a deque import is costly but scales well. realistically this doesn't matter
def load():
    """builds factions, a nested dict eventually containing lists of character Objs.
    """

    if 'factions' in globals():
        raise Exception("load() attempted to overwrite factions dict")

    # recursive function to both load characters (with items) and populate the root factions dict
    def populateFactions(root_list, cd, files):
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
        populateFactions(root_list=root_list, cd=cd[outer_dict], files=files)

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
            # [::-1] reverses the list; populateFactions can root_list.pop() efficiently
            # [:1:-1] slices out the first 2 (junk) elements from the original unreversed list
            populateFactions(root_list=root.split(sep)[:1:-1], cd=factions, files=files)

    return factions

def save(factions=None):
    """writes all character data to local jsons

    Args:
        factions (dict): arbitrarily nested dicts eventually containing lists of character objects
    """
    def get_characters_from_dicts(iterable: list or dict, path=f'.{sep}factions{sep}'):
        # put every nested dict on the stack
        if isinstance(iterable, dict):
            for key, value in iterable.items(): # e.g. path="./factions/sgc/" first
                get_characters_from_dicts(value, path=(path+key+sep))

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

    # TODO P3: implement this
    if factions == None:
        factions = factions
    get_characters_from_dicts(factions)

# TODO P3: less ugly, but still bad
def getChars(charDict):
    """recursively get character objects inside a dictionary

    Args:
        charDict (list): of char_objs

    Returns:
        list: of char_objs
    """
    outList = [] # populated and returned
    def recur(iterable):
        for value in iterable.values():
            if isinstance(value,dict):
                recur(value)
            else:
                # extend operates outside local namespace, += doesn't. TIL
                outList.extend(value)

    recur(charDict)
    return outList

# TODO P3: this shorter version memory leaks???
# somehow outList gets saved between calls, and consecutive calls add to it
# def getChars2(charDict, outList=[]):
#     for value in charDict.values():
#         if isinstance(value,dict):
#             getChars2(value,outList)
#         else:
#             outList += value
#     return outList

# compound_dict = {   1:{2:[3,4]}, 5:{6:{7:[8]}, 9:[0]}   }
# def recur(iterable,output=[]):
#     for value in iterable.values():
#         if isinstance(value,dict):
#             recur(value)
#         else:
#             output += value
#     return output

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


# some golf experiments i'm leaving here
# def getChars2(charDict, outList=[])
#     [getChars2(value, outList) if isinstance(value,dict) else outList.extend(value) for value in iterable.values()]
#     return outList

# def getChars3(charDict):
#     # this is pretty fast, but puts out nested lists
#     return [value if isinstance(value,list) else getChars3(value) if isinstance(value,dict) else value for value in charDict.values()]
