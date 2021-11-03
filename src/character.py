import random
from copy import deepcopy

import races
import classes

# this dict only really gets used in character creation and dmtools
defaults = {
    # biographical information           v (intentionally misspelt)
    "name": "NPC", "race": "human", "clas": "soldier", "faction": "",

    # stats                             (m/s)
    "level": 1, "hp": 10, "temp_hp": 0, "speed": 8.0,

    "attributes": {
        "strength": 8, "dexterity": 8, "constitution": 8, "intelligence": 8, "wisdom": 8, "charisma": 8
    },

    "skills": {
        "acting": 0, "anthropology": 0, "xenoanthropology": 0, "sleightofhand": 0, "stealth": 0,
        "diplomacy": 0, "medicine": 0, "vehicles": 0, "xenotechnology": 0, "technology": 0,
        "insight": 0, "perception": 0, "survival": 0, "tactics": 0, "athletics": 0, "acrobatics": 0
    },

    "slots": {
        "left_hand": None, "right_hand": None, # hands are aliased as "left" or "right"
        "head": None, "chest": None, "legs": None, "belt": None, "boots": None, "gloves": None, "back": None,
    },

    # level_up info
    "attribute_points": 0, "skill_points": 0,
    # inspiration
    "inspiration": 0
}

class Character:
    """Generic character class. Construct with an unpacked **dict
    """
    def __init__(self, **kwargs):
        for key,value in kwargs.items():
            setattr(self,key,value)

    @classmethod
    def new(cls, **kwargs):
        """uncontrolled factory method for first-time character creation
        using this to load character jsons will run unnecessary overhead

        Returns:
            character: created
        """
        char_obj = cls(**(defaults | kwargs))
        char_obj.update()
        return char_obj

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
    # different races should probably just be different classes with different e.g. update_speed methods

    def update_race_and_class(self, race=False, clas=False):
        # functions are simpler, though
        if not hasattr(self,'race_and_class_applied'):
            races.__dict__[race.replace("'","") if race else self.race.replace("'","")](self)
            classes.__dict__[clas if clas else self.clas](self)
            self.race_and_class_applied=True

    def update_bonuses(self):
        # see eof*
        self.bonus_attrs = {attr_name:sum(
            item.bonus_attrs.get(attr_name,0) if item else 0 for item in self.slots.values()
            ) for attr_name in self.attributes}
        self.bonus_skills = {skill_name:sum(
            item.bonus_skills.get(skill_name,0) if item else 0 for item in self.slots.values()
            ) for skill_name in self.skills}

    def update_mods(self):
        self.attr_mods = {attr_name:(self.attributes[attr_name] + self.bonus_attrs[attr_name] - 10) // 2 \
            for attr_name in self.attributes}

    def update_ac(self):
        # hasattr ternary sneakily also checks if the item isn't None
        self.armor_ac = sum(item.bonus_ac if hasattr(item,'bonus_ac') else 0 for item in self.slots.values())
        self.AC = 6 + self.armor_ac + self.attr_mods['dexterity']

    def update_max_hp(self):
        # hp = hit_die+mod for level 1, conMod for each other level
        # standard 5e formula is:
        # hp = (hit_die + conMod) + (level - 1) * (hit_die // 2 + 1 + conMod)
        self.max_hp = (self.hit_die + self.attr_mods['constitution']) + ((self.level - 1) * self.attr_mods['constitution'])

    def update_weight(self):
        # get_weight() does nested item recursion
        self.gear_weight = sum(item.get_weight() if item else 0 for item in self.slots.values())

    def update_speed(self):
        str_mod = self.attr_mods['strength'] + self.bonus_attrs['strength']
        divisor = 100 + str_mod * 50 if str_mod < 6 else 350
        # the goal here is to make strength meaningfully impact the amount of gear someone can carry
        # 1.5 and 100 just felt right for defaults. breakpoints at 21kg, 34, 44, 54...(100*n)**(1/1.5)kg
        # 50 as a multiplier scales pretty accurately given that it's supposed to represent human capability:
        # with the intended max strmod of 5, the max gear someone could carry at 1 m/s is a little under 200kg
        self.speed = 8.0 - self.gear_weight**1.5 // divisor

    def update(self):
        """builds all character meta variables"""
        self.update_bonuses()
        # race/class is done between bonuses and mods because it
        # requires bonuses to exist, and it affects modifier calculation
        self.update_race_and_class()
        self.update_mods()
        # AC and max hp depend on mods
        self.update_ac()
        self.update_max_hp()
        self.update_weight()
        # speed depends on weight and mods
        self.update_speed()
        self.suffix = "'" if self.name[-1] == ("s" or "x") else "'s"

    # TODO P2: this wasn't well tested iirc
    def handle_new_item(self, item, don=True):
        """updates meta-variables whenever a new item is equipped or unequipped

        Args:
            item (item): to handle
            don (bool, optional): True if equipping (donning). Defaults to True.
        """
        # everything gets multiplied by don because sometimes we're unequipping
        don = 1 if don else -1

        # all of these calcs are done outside of their update() methods because it's much more efficient this way
        # this means that changes to the item class could break this method

        # weight and speed first
        self.gear_weight += item.get_weight() * don
        self.update_speed()

        # AC needs recalculation too
        if hasattr(item,'bonus_ac'):
            self.armor_ac += item.bonus_ac * don
            self.AC += item.bonus_ac * don

        # skills are pretty straightforward
        for skill_name,skill_value in item.bonus_skills.items():
            self.bonus_skills[skill_name] += skill_value * don

        # attributes are tricky because of AC and max_hp
        for attr_name,attr_value in item.bonus_attrs.items():
            self.bonus_attrs[attr_name] += attr_value * don
            mod = self.attr_mods[attr_name] = (self.attributes[attr] + self.bonus_attrs[attr] - 10) // 2
            # AC gets recalculated twice sometimes, but it can't really be helped without collapsing Armor into Item
            # this would simplify a lot of the item code, especially around serialization, but it reduces extensibility
            if attr_name == 'dexterity':
                self.AC = 6 + self.armor_ac + mod
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
            item {str} -- to equip
            slot {str} -- to move to
        """
        slot = handle_slot_input(slot)

        if slot in self.slots:
            if self.slots[slot] is None:
                # the actual equip function, everything else is just boilerplate
                self.slots[slot] = item
                self.handle_new_item(item, don=True)

            else:
                print(f"{slot} already contains {self.slots[slot]}")
        else:
            print(f"{slot} invalid. valid slots are:\n", *self.slots)


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
            self.handle_new_item(item, don=False)
            # remove item
            self.slots[slot] = None


    #############################
    # character pretty printing
    #############################
    def show_slots(self):
        """Prints the character's slot contents."""

        print(f"{self.name}{self.suffix} AC is {self.AC} and is wearing:")
        for slot, item in self.slots.items():
            print(f"    {slot}: {item}")
            if item is not None:
                item.show(spacing='        ')
        print("")

    def show_attributes(self):
        """Prints the attributes of the character."""

        print(self.name + self.suffix + " attributes are:")
        for name in self.attributes:
            print(f"    {name}: {self.attributes[name]+self.bonus_attrs[name]}")

    def show_skills(self):
        """Prints the skills of the character."""
        print(self.name + self.suffix + " skills are:")
        for name, skill in self.skills.items():
            print(f"    {name}: {skill}")

    def show(self):
        """Prints the current status of the character."""

        if not hasattr(self,'max_hp'):
            # this happens embarrassingly often
            raise Exception(
                "you used the normal character constructor with the defaults dict instead of the factory method again")

        print(f"{self.name} is a level {self.level} {self.race} {self.clas}.")
        print(f"{self.name} has {self.hp} health, {self.temp_hp} temp health, and {self.max_hp} max health.")

        self.show_attributes()
        self.show_skills()
        self.show_slots()

        print(f"{self.name} has {self.inspiration} inspiration points, " + \
        f"{self.attribute_points} attribute points, and {self.skill_points} skill points.")

    #############################
    #     character combat
    #############################
    # TODO P2: attack function wrapper method?
    def initiative(self, dice=3, die=6):
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

    def hurt(self, d):
        """Hurts the character for d damage.

        Args:
            d (int): damage to deal
        """
        if d > self.temp_hp:
            d -= self.temp_hp
            self.temp_hp = 0
            self.hp -= d
        else:
            self.temp_hp -= d

    #############################
    # character leveling
    #############################
    def randomize_attributes(self):
        """Randomizes character attributes. 4d6 minus lowest roll per attribute
        """
        self.attributes = {name:
        sum(
            sorted(
                [random.randint(1,6) for x in range(4)]
                )[1:]
            )
             for name in self.attributes}

        self.update()

    # everything below is from 2019. it's smelly and largely deprecated. recently updated some of it
    def point_buy_attributes(self, points=27):
        """Starts the point buy process for the character.

        Keyword Arguments:
            points {int} -- The number of points to use in the pointbuy. (default: {27})
        """
        # wrap everything in a copy for aborts
        char_copy = deepcopy(self)
        # set all ability scores to 8
        char_copy.attributes = {attr:8 for attr in self.attributes}

        def bug_player():
            s = input("type an attribute to increment: ").lower()
            if s not in char_copy.attributes.keys():
                print("invalid attribute. attributes are: ", *char_copy.attributes.keys())
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

        self = char_copy


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
                print("invalid attribute. attributes are: ",*char_copy.attributes.keys())

            if char_copy.attributes[s] < 20:
                char_copy.attributes[s] += 1
                char_copy.attribute_points -= 1
            else:
                print("attribute maxed; pick a different attribute")
                char_copy.attribute_points += 1

        # update. int may have been increased enough to effect skill_points
        char_copy.update_mods()
        base_int_mod = (char_copy.attributes['intelligence'] - 10) // 2

        # level_up skills
        char_copy.skill_points += 3 + base_int_mod

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
            if char_copy.skills[s] < 5:
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
        self = char_copy

    def auto_level_up(self, preset=self.clas):

        # acting, anthropology, xenoanthropology, sleightofhand, stealth,
        # diplomacy, medicine, vehicles, xenotechnology, technology,
        # insight, perception, survival, tactics, athletics, acrobatics
        if preset == 'soldier':
            preferred_attrs = 'constitution', 'dexterity', 'strength', 'wisdom', 'intelligence', 'charisma'
            preferred_skills = 'athletics', 'tactics', 'perception', 'acrobatics', 'stealth', 'medicine', 'vehicles', 'survival'

        elif preset == 'scientist':
            preferred_attrs = 'intelligence', 'constitution', 'dexterity', 'wisdom', 'charisma', 'strength'
            preferred_skills = 'technology', 'xenotechnology'

        elif preset == 'archaeologist':
            preferred_attrs = 'wisdom', 'intelligence', 'dexterity', 'charisma', 'constitution', 'strength'
            preferred_skills = 'xenoanthropology', 'anthropology', 'diplomacy', 'insight', 'perception', 'acting'

        # else:
        #     # if nothing is supplied, just exit the function with a random attribute
        #     nonlocal self
        #     return random.choice(tuple(self.attributes.keys()))

        # TODO P2: this is a placeholder. it will also fail if someone's attribute hits a max value
        # prioritizes 3 attrs in order, but keeps them roughly grouped
        if preferred_attrs[0] - preferred_attrs[1] < 2:
            return preferred_attrs[0]
        if preferred_attrs[1] - preferred_attrs[2] < 2:
            return preferred_attrs[1]
        else:
            return preferred_attrs[2]            
            
        char_copy = deepcopy(self)
        char_copy.level += 1

        # level attributes
        if  char_copy.level % 4 == 0:
            char_copy.attribute_points += 2

        for point in range(char_copy.attribute_points):
            char_copy.attributes[   pick_attribute()   ] += 1

        base_int_mod = (char_copy.attributes['intelligence'] - 10) // 2
        char_copy.skill_points += 3 + base_int_mod

        for point in range(char_copy.skill_points):





# *
# updating stats (and attacking) is the only real performance critical part of the code
# i golfed these lines into the method:
# self.bonus_attrs = {attr_name:0 for attr_name in self.attributes}
# self.bonus_skills = {skill_name:0 for skill_name in self.skills}
# for item in self.slots.values():
#     if item:
#         for statName,statValue in item.bonus_attrs.items():
#             self.bonus_attrs[statName] += statValue
#         for statName,statValue in item.bonus_skills.items():
#             self.bonus_skills[statName] += statValue