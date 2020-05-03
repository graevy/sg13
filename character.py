import math
from random import randint

# TODO: simplify constructor:
# class Example:
#     def __init__(self, **kwargs):
#         for name, value in kwargs.iteritems():
#             setattr(self, name, value)

# x = Example(strength="7", diplomacy="9")
# x.strength;

# reference tables

ATTRIBUTES = [
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma",
]
SKILLS = [
    "acting",
    "anthropology",
    "xenoanthropology",
    "diplomacy",
    "medicine",
    "vehicles",
    "technology",
    "xenotechnology",
    "sleightofhand",
    "stealth",
    "insight",
    "perception",
    "survival",
    "tactics",
    "athletics",
    "acrobatics",
]
SLOTS = [
    "leftHand",
    "rightHand",
    "head",
    "body",
    "legs",
    "belt",
    "boots",
    "gloves",
    "back",
]

DEFAULTS = {
    "name": "NPC",
    "race": "human",
    "clas": "soldier",
    "faction": "sgc",
    "level": 1,
    "hitdie": 8,
    "temphp": 0,
    "hp": 8,
    "speed": 10,
    "strength": 10,
    "dexterity": 10,
    "constitution": 10,
    "intelligence": 10,
    "wisdom": 10,
    "charisma": 10,
    "acting": 0,
    "anthropology": 0,
    "xenoanthropology": 0,
    "sleightofhand": 0,
    "stealth": 0,
    "diplomacy": 0,
    "medicine": 0,
    "vehicles": 0,
    "xenotechnology": 0,
    "technology": 0,
    "insight": 0,
    "perception": 0,
    "survival": 0,
    "tactics": 0,
    "athletics": 0,
    "acrobatics": 0,
    "inspiration": 0,
    "leftHand": None,
    "rightHand": None,
    "head": None,
    "body": None,
    "legs": None,
    "belt": None,
    "boots": None,
    "gloves": None,
    "back": None,
    "attributepoints": 0,
    "skillpoints": 0,
}


class Character:
    """Generic character class.
    """

    def __init__(self, data, **kwargs):
        """Character constructor.

        Arguments:
            data {dict} -- A dictionary with any number of the attributes for the character.
        """

        # Pull the name and default value from the default store
        for key, value in DEFAULTS.items():
            # Check if the input has that attribute, otherwise use the default
            if key in data:
                setattr(self, key, data[key])
                self.data[key] = data[key]
            else:
                if key in kwargs:
                    setattr(self, key, kwargs[key])
                else:
                    setattr(self, key, value)
        self.inventory = []
        # Let update do all of the work
        self.update()

    def equip(self, item, slot):
        """Equips the provided item in the provided slot.

        Arguments:
            item {Object} -- The item instance to equip.
            slot {str} -- The slot to equip into, the string is case sensitive.
        """

        if slot in SLOTS:
            if self.gear[SLOTS.index(slot)] is None:
                self.gear[SLOTS.index(slot)] = item

        self.updateSlots()
        self.update()

    def unequip(self, item, slot):
        """Un-equips the provided item from the slot.

        Arguments:
            item {Object} -- The item instance to un-equip.
            slot {str} -- The slot to un-equip from, the string is case sensitive.
        """

        # SLOTS is an identical slots list with strings instead of variables
        if slot in SLOTS:
            if self.gear[SLOTS.index(slot)] is not None:
                self.inventory.append(self.gear[SLOTS.index(slot)])
                self.gear[SLOTS.index(slot)] is None

        self.updateSlots()
        self.update()
    
    def updateSlots(self):
        """Updates the character's slots from gear.
        """
        (
            self.leftHand,
            self.rightHand,
            self.head,
            self.body,
            self.legs,
            self.belt,
            self.boots,
            self.gloves,
            self.back,
        ) = (x for x in self.gear)

    def heal(self, hp=None):
        """Heals the character. The hp provided should always be >= 0

        Keyword Arguments:
            hp {int} -- The amount to heal, default is a full heal. (default: {None})
        """
        if hp is not None and hp > 0:
            self.hp = hp
        else:
            self.hp = self.maxhp
        self.temphp = 0

    def hurt(self, hp=None, temphp=None, totalDamage=None):
        """Hurts the character. All args should be >= 0.

        Keyword Arguments:
            hp {int} -- Optional, how much to subtract from hp. (default: {None})
            temphp {int} -- Optional, how much to subtract from temphp. (default: {None})
            totalDamage {int} -- Preferred, how much total damage to do. (default: {None})
        """
        #If total damage is used.
        if totalDamage is not None:
            #Figure out how much of the damage rolls over.
            hpDamage = totalDamage - self.temphp
            #If nothing rolls over (temphp >= totalDamage) it's really easy.
            if hpDamage <= 0:
                self.temphp -= totalDamage
            else:
                #Otherwise subtract the roll over amount
                self.temphp = 0
                self.hp -= hpDamage
        #Check for temp hp, will not roll over if trying to subtract more than the current temphp
        elif temphp is not None:
            #This is a ternary, if the condition is true, the left side will be assigned, otherwise the right will
            self.temphp = self.temphp - temphp if self.temphp >= temphp else 0
        elif hp is not None:
            self.hp = self.hp - hp if self.hp >= hp else 0


    def grab(self, item, hand=None):
        """Grabs the provided item, optionally specify a hand to grab with.

        Arguments:
            item {Object} -- The item instance to grab.

        Keyword Arguments:
            hand {str} -- String name of the hand to grab with. (default: {None})
        """
        if hand is None:
            if self.rightHand is not None:
                self.rightHand = item
            elif self.leftHand is not None:
                self.leftHand = item
            else:
                print("ope")

        if hand == "right":
            if self.rightHand is not None:
                self.rightHand = item
            else:
                print("ope")

        if hand == "left":
            if self.leftHand is not None:
                self.leftHand = item
            else:
                print("ope")

        self.update()

    def stow(self, item, storageItem=None):
        """Stores an item in the inventory, or in another item.

        Arguments:
            item {Object} -- The object instance to store.

        Keyword Arguments:
            storageItem {Object} -- The optional item to store in. (default: {None})
        """
        if storageItem is None:
            self.inventory.append(item)
        else:
            storageItem.storage.append(item)

    def showInventory(self):
        """Prints the character's inventory.
        """
        for item in self.inventory:
            print("    " + item.name)
            # dmfunctions.printcontents(item)

    def showGear(self):
        """Prints the character's gear.
        """
        for item in self.gear:
            print(item.name)
            # dmfunctions.printcontents(item)

    def showAttributes(self):
        """Prints the attributes of the character.
        """
        for attribute in ATTRIBUTES:
            print(attribute + ": " + str(eval("self." + attribute)))

    def showSkills(self):
        """Prints the skills of the character.
        """
        for skill in SKILLS:
            print(skill + ": " + str(eval("self." + skill)))

    def show(self):
        """Prints the current status of the character.
        """
        if self.name[-1] == "s":
            suffix = "'"
        else:
            suffix = "'s"

        print(
            self.name
            + " is a level "
            + str(self.level)
            + " "
            + self.race
            + " "
            + self.clas
            + "."
        )
        print(
            self.name
            + " has "
            + str(self.hp)
            + " health, "
            + str(self.temphp)
            + " temp health, and "
            + str(self.maxhp)
            + " max health."
        )
        print(self.name + suffix + " attributes are: ")
        for attribute in ATTRIBUTES:
            print("    " + attribute + ": " + str(eval("self." + attribute)))
        # skills
        print(self.name + suffix + " skills are:")
        for skill in SKILLS:
            print("    " + skill + ": " + str(eval("self." + skill)))
        print(self.name + " has an AC of " + str(self.AC) + " and is wearing: ")
        for slot in SLOTS:
            try:
                print("    " + slot + ": " + eval("self." + slot).name)
            except:
                print("    " + slot + ": None")
        print(self.name + suffix + " inventory:")
        self.showInventory()
        print(
            self.name
            + " has "
            + str(self.inspiration)
            + " inspiration points, "
            + str(self.attributepoints)
            + " attribute points, and "
            + str(self.skillpoints)
            + " skill points."
        )

    def initiative(self, dice=3, die=6):
        """Rolls initiative for the character.

        Keyword Arguments:
            dice {int} -- The number of dice to roll. (default: {3})
            die {int} -- The number of sides each die should have. (default: {6})

        Returns:
            int -- The initiative roll.
        """
        return sum([randint(1, die) for x in range(dice)]) + self.dexmod

    def update(self):
        """Updates various attributes of the character.
        """
        self.strmod = (self.strength - 10) // 2
        self.dexmod = (self.dexterity - 10) // 2
        self.conmod = (self.constitution - 10) // 2
        self.intmod = (self.intelligence - 10) // 2
        self.wismod = (self.wisdom - 10) // 2
        self.chamod = (self.charisma - 10) // 2

        self.gear = [
            self.leftHand,
            self.rightHand,
            self.head,
            self.body,
            self.legs,
            self.belt,
            self.boots,
            self.gloves,
            self.back,
        ]

        self.armor = [
            self.head,
            self.body,
            self.legs,
            self.belt,
            self.boots,
            self.gloves,
            self.back,
        ]

        # character data
        self.gearweight = 0.0
        for item in self.gear and self.inventory:
            if hasattr(item, "weight"):
                gearweight += item.weight

            # TODO recursive function to calculate gear weight from nested items
            for storeditem in item.storage:
                if hasattr(storeditem, "weight"):
                    gearweight += storeditem.weight

        self.armorAC = 0
        for item in self.armor:
            if hasattr(item, "bonusAC"):
                armorAC += item.bonusAC
        self.AC = 6 + self.dexmod + self.armorAC

        self.attributes = [
            self.strength,
            self.dexterity,
            self.constitution,
            self.intelligence,
            self.wisdom,
            self.charisma,
        ]
        self.skills = [
            self.acting,
            self.anthropology,
            self.xenoanthropology,
            self.diplomacy,
            self.medicine,
            self.vehicles,
            self.technology,
            self.xenotechnology,
            self.sleightofhand,
            self.stealth,
            self.insight,
            self.perception,
            self.survival,
            self.tactics,
            self.athletics,
            self.acrobatics,
        ]

        # hp = hitdie+mod for level 1, add smaller bonus for each level
        # standard 5e formula is:
        # self.hp = (self.hitdie + self.conmod) + (self.level - 1) * (self.hitdie // 2 + 1 + self.conmod)
        self.maxhp = (self.hitdie + self.conmod) + (self.level - 1) * (
            self.conmod
        )

    def randomizeAttributes(self):
        """Randomizes the attributes of the character.
        """
        (
            self.strength,
            self.dexterity,
            self.constitution,
            self.intelligence,
            self.wisdom,
            self.charisma,
        ) = (
            sum(sorted([randint(1, 6) for x in range(4)])[1:])
            for x in self.attributes
        )

        self.update()

    def pointBuyAttributes(self, points=27):
        """Starts the point buy process for the character.

        Keyword Arguments:
            points {int} -- The number of points to use in the pointbuy. (default: {27})
        """
        (
            self.strength,
            self.dexterity,
            self.constitution,
            self.intelligence,
            self.wisdom,
            self.charisma,
        ) = (8 for x in self.attributes)
        self.update()

        while points > 0:

            s = input("type an attribute to += 1: ")
            if self.attributes[ATTRIBUTES.index(s)] >= 15:
                self.attributes[ATTRIBUTES.index(s)] += 1

                if self.attributes[ATTRIBUTES.index(s)] > 13:
                    points -= 2
                else:
                    points -= 1
            else:
                print("attribute at starting cap (15)")

    def levelUp(self):
        """Levels up the character.
        """
        self.level += 1

        # level attributes
        self.attributepoints += 1
        print(
            "current attributes: strength "
            + str(self.strength)
            + ", dexterity "
            + str(self.dexterity)
            + ", constitution "
            + str(self.constitution)
            + ", intelligence "
            + str(self.intelligence)
            + ", wisdom "
            + str(self.wisdom)
            + ", charisma "
            + str(self.charisma)
        )

        while self.attributepoints > 0:
            s = input(
                "type an attribute (or leave blank to exit) to increase by 1: "
            )

            if s == "":
                break

            if self.attributes[ATTRIBUTES.index(s)] < 20:
                self.attributes[ATTRIBUTES.index(s)] += 1
                self.attributepoints -= 1
            else:
                print("attribute maxed; pick a different attribute")
                self.attributepoints += 1

        # update attributes from new list
        (
            self.strength,
            self.dexterity,
            self.constitution,
            self.intelligence,
            self.wisdom,
            self.charisma,
        ) = (x for x in self.attributes)

        # update character now in case int is increased enough to effect skillpoints
        self.update()

        # levelup skills
        self.skillpoints += 3 + self.intmod

        while self.skillpoints > 0:
            s = input(
                "type a skill (or leave blank to exit) to increase by 1: "
            )

            if s == "":
                break
            # SKILLS is a copy of self.skills with strings instead of variables;
            # self.skills[SKILLS.index(s)] selects the appropriate skill via user input
            if s not in SKILLS:
                print("that is not a skill")

            # check to make sure the skill isn't maxed out
            elif self.skills[SKILLS.index(s)] < 5:
                # skills above 2 cost 2 to level instead of 1
                if self.skills[SKILLS.index(s)] > 2:
                    if self.skillpoints > 1:
                        self.skills[SKILLS.index(s)] += 1
                        self.skillpoints -= 2
                    else:
                        print("not enough to points level this skill")
                # base case: increment skill and decrement skillpoints
                else:
                    self.skills[SKILLS.index(s)] += 1
                    self.skillpoints -= 1
            else:
                print("skill maxed; pick a different skill")

        (
            self.acting,
            self.anthropology,
            self.xenoanthropology,
            self.diplomacy,
            self.medicine,
            self.vehicles,
            self.technology,
            self.xenotechnology,
            self.sleightofhand,
            self.stealth,
            self.insight,
            self.perception,
            self.survival,
            self.tactics,
            self.athletics,
            self.acrobatics,
        ) = (x for x in self.skills)

        # update character again
        self.update()
