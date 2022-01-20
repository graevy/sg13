import random
from copy import deepcopy
import json
import os

import race
import class_
import rolls
import cfg.dirs

MAX_LEVEL = 20
MAX_ATTR = 20
MAX_SKILL = 5
BASE_SKILL_POINTS = 3
BASE_AC = 6
MELEE_RANGE = 3
DEFAULT_POINT_BUY_POINTS = 27
DEFAULT_ATTR = 8
DEFAULT_SKILL = 0
MAX_BONUS_AC_FROM_COVER = 4
COVER_INTERVAL = 100 // MAX_BONUS_AC_FROM_COVER
RANGE_EXPONENT = 2 # higher value makes ranged attacks hit less often. below 1 and they're better than melee

# much of the code is duplicated for performing the same actions on attributes and skills.
# i'm forced to ask myself why keeping them separate is necessary, and i'm drawing a blank.
# it's a pretty minor refactor. the biggest issue i see is handling skill/attr points for leveling.
# it would mitigate the coding-ttrpg "attribute" name collision
# i need to think more about it. 


class Character:
    """Generic character class. Create new instances with create(). Load saved instances with __init__()
    """
    def __init__(self, attrs: dict):
        """for loading saved characters"""
        self.__dict__ |= attrs

    @classmethod
    def create(cls, attrs: dict):
        """uncontrolled factory method for first-time character creation
        using this to load character jsons will run unnecessary overhead

        Returns:
            character: created
        """#           e.g. /races/human/human.json
        with open(cfg.dirs.RACES_DIR + attrs.get('race','human') + os.sep + "defaults.json") as f:
            char_obj = cls(json.load(f) | attrs)

        char_obj.update()
        return char_obj

    def __str__(self):
        return f'{self.name}: {self.faction}'

    # these are a solid maybe
    # @classmethod
    # def load(cls, path=None):
    #     if path is None:
    #         path = '.' + os.sep + self.faction.replace('/',os.sep) + os.sep + self.name + '.json'
    #     with open(path, encoding='utf-8') as f:
    #         return cls(json.load(f))

    # def save(self):
    #     attrs = vars(self)
    #     attrs['slots'] = {slot:item.get_json() if item else None for slot,item in self.slots.items()}
    #     with open(f'.{os.sep}factions{self.faction.replace('/',os.sep)}{os.sep}.json', 'w+', encoding='utf-8') as f:
    #         json.dump(attrs, f)

    def get_json(self):
        """Creates and returns a (JSON serializable, writeable) dict of the character.

        Returns:
            dict -- of the character's attributes.
        """
        attrs = vars(self)
        # item.get_json does recursion
        attrs['slots'] = {slot:item.get_json() if item else None for slot,item in self.slots.items()}
        return attrs

    #############################
    #### stat update methods ####
    #############################
    # TODO P3: update_bonuses/update_mods should utilize updateBonus/updateMod methods,
    # this would harden e.g. handle_new_item against e.g. item/feat extensibility. in the same vein,
    # different races should probably just be different classes with different e.g. update_speed methods?

    def update_class_(self):
        if not hasattr(self,'class_applied'):
            class_dict = class_.load_class_(self.class_)

            self.hit_die = class_dict['hit_die']

            for attr,bonus in class_dict['bonus_attrs'].items():
                self.bonus_attrs[attr] += bonus
            for skill,bonus in class_dict['bonus_skills'].items():
                self.bonus_skills[skill] += bonus

            self.class_applied = True

    def update_bonus(self, attr_name, value):
        self.bonus_attrs[attr_name] = self.bonus_attrs.setdefault(attr_name,0) + value

    def update_mod(self, attr_name):
        self.attr_mods[attr_name] = self.attributes[attr_name] + self.bonus_attrs[attr_name] - 10 >> 1

    # TODO P3: this became very horrifying very quickly. i'm sorry.
    # i've left some code at EOF * as the start of a potential alternative?
    def update_bonuses(self):
        self.bonus_attrs = {attr_name:self.bonus_attrs.setdefault(attr_name,0) + 
        sum(
            item.bonus_attrs[attr_name] for item in self.slots.values() if item
            ) for attr_name in self.attributes}

        self.bonus_skills = {skill_name:self.bonus_skills.setdefault(skill_name,0) + 
        sum(
            item.bonus_skills[skill_name] for item in self.slots.values() if item
            ) for skill_name in self.skills}


    def update_mods(self):
        self.attr_mods = {attr_name:self.attributes[attr_name] + self.bonus_attrs[attr_name] - 10 >> 1
            for attr_name in self.attributes}

    def update_ac(self):
        self.armor_ac = sum(item.bonus_ac for item in self.slots.values() if hasattr(item,'bonus_ac'))
        self.ac = BASE_AC + self.armor_ac + self.attr_mods['dexterity']

    def update_max_hp(self):
        # hp = hit_die+mod for level 1, conMod for each other level
        # standard 5e formula is:
        # hp = (hit_die + conMod) + (level - 1) * (hit_die // 2 + 1 + conMod)
        self.max_hp = (self.hit_die + self.attr_mods['constitution']) + ((self.level - 1) * self.attr_mods['constitution'])

    def update_weight(self):
        # get_weight() does nested item recursion
        self.gear_weight = sum(item.get_weight() for item in self.slots.values() if item)

    def update_speed(self):
        str_mod = self.attr_mods['strength']

        if str_mod < 0:
            divisor = 50
        elif str_mod > 5:
            divisor = 350
        else:
            divisor = 100 + str_mod * 50
        # the goal here is to make strength meaningfully impact the amount of gear someone can carry
        # 1.5 and 100 just felt right for defaults. breakpoints at 21kg, 34, 44, 54...(100*n)**(1/1.5)kg
        # 50 as a multiplier scales pretty accurately given that it's supposed to represent human capability:
        # with the intended max strmod of 5, the max gear someone could carry at 1 m/s is a little under 200kg
        self.speed = self.base_speed - self.gear_weight**1.5 // divisor

    def update(self):
        """builds all character meta variables"""
        self.update_bonuses()
        # class_ is done between bonuses and mods because it
        # requires bonuses to exist, and it affects modifier calculation
        self.update_class_()
        self.update_mods()
        # ac and max hp depend on mods
        self.update_ac()
        self.update_max_hp()
        self.update_weight()
        # speed depends on weight and mods
        self.update_speed()
        self.suffix = "'" if self.name[-1] == ("s" or "x") else "'s"

    # TODO P3: make this use the new update_mod and update_bonus methods
    # it just doesn't build off of the other methods at all. should be simplified
    def handle_new_item(self, item, equipping=True):
        """updates meta-variables whenever a new item is equipped or unequipped

        Args:
            item (item): to handle
            equipping (bool, optional): True if equipping. Defaults to True.
        """
        equipping = 1 if equipping else -1

        # all of these calcs are outside of their update() methods because it's much more efficient this way
        # this means that changes to the item class could break this method

        # weight and speed first
        self.gear_weight += item.get_weight() * equipping
        self.update_speed()

        # ac needs recalculation too
        if hasattr(item,'bonus_ac'):
            self.armor_ac += item.bonus_ac * equipping
            self.ac += item.bonus_ac * equipping

        # skills are pretty straightforward
        for skill_name,skill_value in item.bonus_skills.items():
            self.bonus_skills[skill_name] += skill_value * equipping

        # attributes are tricky because of ac and max_hp
        for attr_name,attr_value in item.bonus_attrs.items():
            self.bonus_attrs[attr_name] += attr_value * equipping
            mod = self.attr_mods[attr_name] = (self.attributes[attr] + self.bonus_attrs[attr] - 10) // 2
            # ac gets recalculated twice sometimes, but it can't really be helped without collapsing Armor into Item
            # this would simplify a lot of the item code, especially around serialization, but it reduces extensibility
            if attr_name == 'dexterity':
                self.ac = BASE_AC + self.armor_ac + mod
            if attr_name == 'constitution':
                self.max_hp = (self.hit_die + mod) + \
                ((self.level - 1) * mod)

    #############################
    # character item handling
    #############################
    @staticmethod
    def handle_slot_input(slot):
        slot = slot.strip().lower()
        if slot[:4] == "left" or slot[:2] == "lh":
            slot = "left_hand"
        if slot[:5] == "right" or slot[:2] == "rh":
            slot = "right_hand"
        return slot

    def equip(self, item, slot):
        """moves an item to a character object's slot.

        Arguments:
            item {item.Item} -- to equip
            slot {str} -- to move to
        """
        slot = self.handle_slot_input(slot)

        if slot in self.slots:
            if self.slots[slot] is None:
                # the actual equip function, everything else is just boilerplate
                self.slots[slot] = item
                self.handle_new_item(item, equipping=True)

            else:
                print(f"{slot} already contains {self.slots[slot]}")
        else:
            print(f"'{slot}' invalid. valid slots are:\n    {', '.join(self.slots)}")


    def stow(self, slot, container):
        """Stores a character object's slot's item in another item.

        Arguments:
            item {Object} -- to store.

        Keyword Arguments:
            container {Object} -- to store in.
        """
        slot = handle_slot_input(slot)
        item = self.slots[slot]

        if item.store(container):
            self.handle_new_item(item, equipping=False)
            # remove item
            self.slots[slot] = None


    #############################
    # character pretty printing
    #############################
    def show_slots(self):
        """Prints the character's slot contents."""

        print(f"{self.name}{self.suffix} ac is {self.ac} and is wearing:")
        for slot, item in self.slots.items():
            print(f"    {slot}: {item}")
            if item is not None:
                item.show(spacing='        ')
        print("")

    def show_attributes(self):
        """Prints the attributes of the character."""

        print(self.name + self.suffix + " attributes are:")
        for name in self.attributes:
            print(f"    {name}: {self.attributes[name] + self.bonus_attrs[name]}")

    def show_skills(self):
        """Prints the skills of the character."""

        print(self.name + self.suffix + " skills are:")
        for name, skill in self.skills.items():
            print(f"    {name}: {skill}")

    def show(self):
        """Prints the current status of the character."""

        print(f"{self.name} is a level {self.level} {self.race} {self.class_}.")
        print(f"{self.name} has {self.hp} health, {self.temp_hp} temp health, and {self.max_hp} max health.")

        self.show_attributes()
        self.show_skills()
        self.show_slots()

        print(f"{self.name} has {self.inspiration} inspiration points, " + \
        f"{self.attribute_points} attribute points, and {self.skill_points} skill points.")

    #############################
    #   character interaction   #
    #############################

    def skill_check(self, stat, dc, roll_fn=rolls.IIId6):
        return True if roll_fn() + self.skills[stat] + self.bonus_skills[stat] >= dc else False

    # TODO P2: attack function wrapper method?
    def initiative(self, dice=rolls.dice, die=rolls.die):
        """Rolls initiative for the character.

        Keyword Arguments:
            dice {int} -- The number of dice to roll. (default: {3})
            die {int} -- The number of sides each die should have. (default: {6})

        Returns:
            int -- The initiative roll.
        """
        return sum(random.randint(1, die) for x in range(dice)) + self.attr_mods['dexterity']

    def heal(self, h=None):
        """Heals the character for h health.

        Args:
            h (int, optional): Hitpoints to heal; leave blank to full heal. Defaults to None.
        """
        # if we're doing a basic full heal...
        if h == None:
            self.hp = self.max_hp
        else:
            self.hp += h
        # (don't overheal)
        if self.hp > self.max_hp:
            self.hp = self.max_hp


    def attack(self, defender, weapon=None, distance=0, cover=0):
        """self rolls against defender with weapon from distance

        Args:
            defender (Character): Character defending
            weapon (Weapon): Attacker's weapon. Defaults to None.
            distance (int, optional): Attack distance. Defaults to 0.
            cover (int, optional): % defender is covered. Defaults to None.
        """
        # factoring distance
        distance_mod = 1 - (distance / weapon.range) ** RANGE_EXPONENT
        if distance_mod < 0:
            distance_mod = 0.0

        # factoring cover
        cover_mod = cover // COVER_INTERVAL

        # fetch weapon
        if weapon is None:
            if self.slots['right_hand'] is None:
                if self.slots['left_hand'] is None:
                    # TODO P3: i'm thinking about improvised weaponry?
                    # TODO P2: untested
                    with open(cfg.dirs.ITEMS_DIR + 'fist.json') as fist:
                        weapon = item.Weapon(json.load(fist))
                else:
                    weapon = self.slots['left_hand']
            else:
                weapon = self.slots['right_hand']

        # weapon mods to hit
        match weapon.proficiency:
            case 'strength':
                weapon_hit_mod = self.attr_mods['strength']
            case 'dexterity':
                weapon_hit_mod = self.attr_mods['dexterity']
            case 'finesse':
                weapon_hit_mod = max(self.attr_mods['strength'], self.attr_mods['dexterity'])

        # hit calculation
        hit_roll = rolls.IIId6() + weapon_hit_mod

        # dual wield penalty
        if self.slots['left_hand'] and self.slots['right_hand']:
            hit_roll -= 2

        # qc penalty for long range weapons
        if weapon.cqc_penalty > 0 and distance > 3:
            hit_roll -= 2 * weapon.cqc_penalty
            print("close combat weapon penalty applied")

        # does the attack hit?
        if hit_roll > (defender.ac + cover_mod):
            # damage calculation
            damage = (
                round(
                    rolls.roll(2, weapon.damage // 2) * distance_mod
                )
            )

            print(f"{self.name} rolled {hit_roll} to hit {defender.name} for {damage}")

            defender.hurt(totalDamage=damage)

            print(f"{defender.name} is at {defender.hp} health")

        else:
            print("miss!")


    def hurt(self, d):
        """Hurts the character for d damage.

        Args:
            d (int): damage to deal
        """
        if d > self.temp_hp:
            self.hp -= d - self.temp_hp
            self.temp_hp = 0
        else:
            self.temp_hp -= d

    #############################
    # character leveling
    #############################
    def randomize_attributes(self, dice=rolls.dice, die=rolls.die):
        """Randomizes character attributes. 4d6 minus lowest roll per attribute
        """
        self.attributes = {name:
        sum(
            # sorted()[1:] quickly drops the lowest value
            sorted(
                random.randint(1,die) for x in range(dice+1)
                )[1:]
            )
             for name in self.attributes}

        self.update()

    # smelly
    def point_buy_attributes(self, points=DEFAULT_POINT_BUY_POINTS):
        """Starts the point buy process for the character.

        Keyword Arguments:
            points {int} -- The number of points to use in the pointbuy. (default: {DEFAULT_POINT_BUY_POINTS})
        """
        # wrap everything in a copy for aborts
        char_copy = deepcopy(self)
        # set all ability scores to DEFAULT_ATTR
        char_copy.attributes = {attr:DEFAULT_ATTR for attr in self.attributes}

        def bug_player():
            s = input("type an attribute to increment: ").lower()
            if s not in char_copy.attributes:
                print("invalid attribute. attributes are: ", *char_copy.attributes)
                return False
            return s

        # it's possible in some point totals to have all attributes above 12 and still have 1 point left;
        # buying any more attributes becomes impossible
        def is_stalled():
            if points != 1:
                return False
            for attribute in char_copy.attributes.values():
                if attribute < 13:
                    return False
            return True

        char_copy.show_attributes()

        while points > 0:

            s = bug_player()

            # s is only False when you put in a bad attribute
            if not s:
                continue
            if is_stalled():
                break

            if char_copy.attributes[s] < 15:
                if char_copy.attributes[s] < 13:
                    points -= 1
                    char_copy.attributes[s] += 1
                    print(f'Attribute {s} increased by 1. {points} points remaining.')
                elif points > 1:
                    points -= 2
                    char_copy.attributes[s] += 1
                else:
                    print(f'Not enough points to level {s}. {points} points remaining.')
            else:
                print(f"attribute {s} at starting cap (15)")

        self.__dict__ = char_copy.__dict__


    # TODO P2: redo this whole function tbh
    def level_up(self):
        """levels the character"""

        char_copy = deepcopy(self)
        char_copy.level += 1

        # level attributes
        if  char_copy.level % 4 == 0:
            char_copy.attribute_points += 2
            char_copy.show_attributes()

        while char_copy.attribute_points > 0:
            s = input("type an attribute (or leave blank to exit) to increase by 1: ").lower()

            if s == "":
                break

            if s not in char_copy.attributes:
                print("invalid attribute. attributes are:",*char_copy.attributes)

            if char_copy.attributes[s] < MAX_ATTR:
                char_copy.attributes[s] += 1
                char_copy.attribute_points -= 1
            else:
                print("attribute maxed; pick a different attribute")
                char_copy.attribute_points += 1

        # update. int may have been increased enough to effect skill_points
        char_copy.update_mods()
        base_int_mod = (char_copy.attributes['intelligence'] - 10) // 2

        # level_up skills
        char_copy.skill_points += BASE_SKILL_POINTS + base_int_mod

        char_copy.show_skills()
        while char_copy.skill_points > 0:
            s = input(
                f"You have {char_copy.skill_points} skill points. \n"+\
                "Type skills to list skills. Leave blank to exit (saving points). \n" +\
                "Type a skill to increase: "
            )

            if s == "":
                break

            if s == 'skills':
                char_copy.show_skills()
                continue

            if s not in char_copy.skills:
                print("that's not a skill")
                continue

            # check to make sure the skill isn't maxed out
            if char_copy.skills[s] < MAX_SKILL:
                # skills above 2 cost 2 to level instead of 1
                if char_copy.skills[s] > 2:
                    if char_copy.skill_points > 1:
                        char_copy.skills[s] += 1
                        char_copy.skill_points -= 2
                    else:
                        print("not enough to points level this skill")
                # base case: increment skill and decrement skill_points
                else:
                    char_copy.skills[s] += 1
                    char_copy.skill_points -= 1
            else:
                print("skill maxed; pick a different skill")

        char_copy.update()
        self.__dict__ = char_copy.__dict__


    def level_up_auto(self, levels=1):
        """automatically level a character based off class-supplied biases

        Args:
            levels (int, optional): to level the character by. Defaults to 1.

        Raises:
            Exception: attributes are all at maximum
            Exception: skills are all at maximum
        """

        with open(cfg.dirs.CLASS_ES_DIR + self.class_ + '.json', encoding='utf-8') as f:
            class_dict = json.load(f)
            attr_weights = class_dict['attr_weights']
            skill_weights = class_dict['skill_weights']

        # wrap everything in a copy of self, in case the levelup fails
        char_copy = deepcopy(self)

        # level attributes

        # calculate # of points to allocate. 2 every 4 levels
        quotient, remainder = divmod(levels,4)

        # Δ attribute_points is levels // 4, plus any remainder that pushes char_copy.level above a multiple of 4
        # expressed by the equation:    (levels//4)         level+remainder//4
        # char_copy.attribute_points += (quotient + (char_copy.level + remainder >> 2)) * 2
        # simplified to:
        char_copy.attribute_points += quotient * 2 + (char_copy.level + remainder >> 1)

        char_copy.level += levels

        # attribute selection
        while char_copy.attribute_points > 0:
            attrs = char_copy.attributes
            # so, to choose which attribute to level, sort them (low to high) by 
            # their value: attrs[attr], minus their class-supplied weighting: attr_weights[attr],
            # modified by the formula: (weight * (level + max level) >> 5)
            # this means that attributes with a higher weight get put first. it scales with character level,
            # allowing for at most 12 points at max level between highest and lowest attribute

            # key takes a function, which takes each iterable elem as an arg (like a for loop), 
            # and sorts by the function's output.

            # using dict.get(value,0) allows for support for shorter weights dicts. e.g. a scientist
            # doesn't need 'strength':0, and could just have {'tecnhology':10} for a skill weights dict.

            order = sorted(attrs, key=lambda attr: attrs[attr] - (attr_weights.get(attr,0) * (char_copy.level + MAX_LEVEL) >> 5))

            # we still need to make sure that we respect the max attr value
            for idx,attr in enumerate(order):
                if attrs[attr] >= MAX_ATTR:
                    # determine the character's attributes aren't all maxed
                    if idx >= len(attrs) - 1:
                        raise Exception(f"{char_copy.name} has all attrs >= {MAX_ATTR}.")
                    continue
                # pick the first attribute in the ordered list (that is a valid levelup attr)
                attrs[attr] += 1
                char_copy.attribute_points -= 1
                break

        # repeating myself for skills

        # level skills
        base_int_mod = (char_copy.attributes['intelligence'] - 10) // 2 
        char_copy.skill_points += (BASE_SKILL_POINTS + base_int_mod) * levels

        # see above
        while char_copy.skill_points > 0:
            skills = char_copy.skills
            order = sorted(skills, key=lambda skill: skills[skill] - skill_weights.get(skill,0))

            for idx,skill in enumerate(order):
                if skills[skill] >= MAX_SKILL:
                    if idx >= len(skills) - 1:
                        raise Exception(f"{char_copy.name} has all skills >= {MAX_SKILL}.")
                    continue
                skills[skill] += 1
                char_copy.skill_points -= 1
                break

        char_copy.update()

        # using __dict__ sort of like dereferencing
        self.__dict__ = char_copy.__dict__



# * updating stats (and attacking) is the only real performance critical part of the code
# def update_bonuses(self):
#     for slot in self.slots.values():
#         if slot is not None:
#             for attr_name, attr_value in slot.bonus_attrs.items():
#                 self.update_bonus(self.bonus_attrs, )

#     self.bonus_attrs = {attr_name:self.update_bonus(self.bonus_attrs, attr_name, 
#         sum(item.bonus_attrs[attr_name] if item else 0 for item in self.slots.values())) for attr_name in self.attributes}
#     self.bonus_skills = {skill_name:self.update_bonus(self.bonus_skills, skill_name, 
#         sum(item.bonus_skills[skill_name] if item else 0 for item in self.slots.values())) for skill_name in self.skills}

# def update_bonuses(self):
#     self.bonus_attrs = {attr_name:0 for attr_name in self.attributes}
#     self.bonus_skills = {skill_name:0 for skill_name in self.skills}
#     for item in self.slots.values():
#         if item:
#             for statName,statValue in item.bonus_attrs.items():
#                 self.bonus_attrs[statName] += statValue
#             for statName,statValue in item.bonus_skills.items():
#                 self.bonus_skills[statName] += statValue
