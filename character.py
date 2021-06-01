# pylint: disable=no-member

import math
from random import randint

characterCreationDefaults = {
    # basic information
    "name": "NPC", "race": "human", "clas": "soldier", "faction": "sgc",
    # stats
    "level": 1, "hitdie": 8, "hp": 8, "temphp": 0, "speed": 10,
    # attributes
    "strength": 10, "dexterity": 10, "constitution": 10, "intelligence": 10, "wisdom": 10, "charisma": 10,
    # skills
    "acting": 0, "anthropology": 0, "xenoanthropology": 0, "sleightofhand": 0, "stealth": 0, "diplomacy": 0, "medicine": 0, "vehicles": 0,
    "xenotechnology": 0, "technology": 0, "insight": 0, "perception": 0, "survival": 0, "tactics": 0, "athletics": 0, "acrobatics": 0, "inspiration": 0,
    # hands
    "leftHand": None, "rightHand": None,
    # gear
    "head": None, "chest": None, "legs": None, "belt": None, "boots": None, "gloves": None, "back": None,
    # levelup info
    "attributepoints": 0, "skillpoints": 0
}


class Character:
    """Generic character class.
    """
    

    def __init__(self, data, **kwargs):
        self.data = data

        for k, v in characterCreationDefaults.items():
            setattr(self, k, v)
        for k, v in data.items():
               if k in characterCreationDefaults.keys():
                   setattr(self, k, v)
        for key in kwargs:
           setattr(self, key, kwargs[key])

        self.suffix = "'" if self.name[-1] == "s" or "x" else "'s"
        self.inventory = []
        # update() builds lists like self.gear, self.attributes, etc
        self.update()

    def getJSON(self):
        """Creates and returns a JSON writable version of the character.

        Returns:
            dict -- A dictionary version of the character's data.
        """
        result = {}
        for key in characterCreationDefaults.keys():
            result[key] = getattr(self, key)
        return result

    def update(self):
        """Updates various attributes of the character.
        """
        self.strmod = (self.strength - 10) // 2
        self.dexmod = (self.dexterity - 10) // 2
        self.conmod = (self.constitution - 10) // 2
        self.intmod = (self.intelligence - 10) // 2
        self.wismod = (self.wisdom - 10) // 2
        self.chamod = (self.charisma - 10) // 2

        self.gear = {
            'leftHand':self.leftHand,
            'rightHand':self.rightHand,
            'head':self.head,
            'chest':self.chest,
            'legs':self.legs,
            'belt':self.belt,
            'boots':self.boots,
            'gloves':self.gloves,
            'back':self.back
        }

        self.armor = {
            'head':self.head,
            'chest':self.chest,
            'legs':self.legs,
            'belt':self.belt,
            'boots':self.boots,
            'gloves':self.gloves,
            'back':self.back
        }

        self.gearweight = 0.0
        # character data
        for item in self.gear.values() and self.inventory:
            if hasattr(item, "weight"):
                self.gearweight += item.weight

            # TODO recursive function to calculate gear weight
            for storeditem in item.storage:
                if hasattr(storeditem, "weight"):
                    gearweight += storeditem.weight

        self.armorAC = 0
        for item in self.armor:
            if hasattr(item, "bonusAC"):
                armorAC += item.bonusAC
        self.AC = 6 + self.dexmod + self.armorAC

        self.attributes = {
            'strength':self.strength,
            'dexterity':self.dexterity,
            'constitution':self.constitution,
            'intelligence':self.intelligence,
            'wisdom':self.wisdom,
            'charisma':self.charisma
        }

        self.skills = {
            'acting':self.acting,
            'anthropology':self.anthropology,
            'xenoanthropology':self.xenoanthropology,
            'diplomacy':self.diplomacy,
            'medicine':self.medicine,
            'vehicles':self.vehicles,
            'technology':self.technology,
            'xenotechnology':self.xenotechnology,
            'sleightofhand':self.sleightofhand,
            'stealth':self.stealth,
            'insight':self.insight,
            'perception':self.perception,
            'survival':self.survival,
            'tactics':self.tactics,
            'athletics':self.athletics,
            'acrobatics':self.acrobatics
        }

        # hp = hitdie+mod for level 1, conmod for each other level
        # standard 5e formula is:
        # self.hp = (self.hitdie + self.conmod) + (self.level - 1) * (self.hitdie // 2 + 1 + self.conmod)
        self.maxhp = (self.hitdie + self.conmod) + ((self.level - 1) * self.conmod)

    def equip(self, item, slot):
        """Equips the provided item in the provided slot.

        Arguments:
            item {Object} -- The item instance to equip.
            slot {str} -- The slot to equip into.
        """
        slot = slot.lower().strip()

        if slot == ("left" or "lefthand"):
            slot = "leftHand"
        if slot == ("right" or "righthand"):
            slot = "rightHand"

        if slot in self.gear.keys() and getattr(self, slot) is None:
            setattr(self, slot, item)
        else:
            print("invalid equip slot")

        self.update()

    def unequip(self, slot):
        """Un-equips the provided item from the slot.

        Arguments:
            slot {str} -- The slot to un-equip from.
        """

        if slot in self.gear.keys() and getattr(self, slot) is not None:
            self.inventory.append(getattr(self, slot))
            setattr(self, slot, None)
        else:
            print("invalid unequip slot")

        self.update()

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
        # If total damage is used.
        if totalDamage is not None:
            # Figure out how much of the damage rolls over.
            hpDamage = totalDamage - self.temphp
            # If nothing rolls over (temphp >= totalDamage) it's really easy.
            if hpDamage <= 0:
                self.temphp -= totalDamage
            else:
                # Otherwise subtract the roll over amount
                self.temphp = 0
                self.hp -= hpDamage
        # Check for temp hp, will not roll over if trying to subtract more than the current temphp
        elif temphp is not None:
            # This is a ternary, if the condition is true, the left side will be assigned, otherwise the right will
            self.temphp = self.temphp - temphp if self.temphp >= temphp else 0
        elif hp is not None:
            self.hp = self.hp - hp if self.hp >= hp else 0


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
        # TODO: recursion
        print("Inventory:")
        for item in self.inventory:
            print("    " + item.name)
        print("")

    def showGear(self):
        """Prints the character's gear.
        """
        # TODO: recursion
        print(self.name + " has an AC of " + str(self.AC) + " and is wearing: ")
        for slot, item in self.gear.items():
            print(slot + ": " + str(item))
        print("")

    def showAttributes(self):
        """Prints the attributes of the character.
        """
        print(self.name + self.suffix + " attributes are: ")
        for name, attribute in self.attributes.items():
            print(name + ": " + str(attribute))
        print("")

    def showSkills(self):
        """Prints the skills of the character.
        """
        print(self.name + self.suffix + " skills are: ")
        for name, skill in self.skills.items():
            print(name + ": " + str(skill))
        print("")

    def show(self):
        """Prints the current status of the character.
        """

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
        self.showAttributes()
        self.showSkills()
        self.showGear()
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
        return (sum([randint(1, die) for x in range(dice)]) + self.dexmod)

    def randomizeAttributes(self):
        """Randomizes character attributes. 4d6 minus lowest roll per attribute
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
        ) = (8 for x in self.attributes.values())
        self.update()

        def bug_player():
            s = input("type an attribute to increment: ".lower())
            if s not in self.attributes.keys():
                print("invalid attribute. attributes are: " + str(self.attributes.keys())[11:-2])
                return False
            return s

        # it's possible in some point totals to have all attributes above 12 and still have 1 point left;
        # buying any more attributes becomes impossible
        def is_stalled():
            if points != 1:
                return False
            for attribute in self.attributes.values():
                if attribute < 13:
                    return False
            return True

        while points > 0:

            s = bug_player()

            # s is only False when you put in a bad attribute
            if not s:
                continue
            if is_stalled():
                self.attributepoints += 1
                break

            if self.attributes[s] < 15:
                points -= 1 if self.attributes[s] < 13 else 2
            else:
                print("attribute at starting cap (15)")


    def levelUp(self):
        """Levels up the character.
        """
        self.level += 1

        # level attributes
        if  self.level % 4 == 0:
            self.attributepoints += 2
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
            s = input("type an attribute (or leave blank to exit) to increase by 1: ").lower()

            if s == "":
                break

            if s not in self.attributes.keys():
                print("invalid attribute. attributes are: " + str(self.attributes.keys())[11:-2])

            if self.attributes[s] < 20:
                self.attributes[s] += 1
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
        ) = (x for x in self.attributes.values())

        # update character now in case int is increased enough to effect skillpoints
        self.update()

        # levelup skills
        self.skillpoints += 3 + self.intmod

        while self.skillpoints > 0:
            s = input(
                "You have "+str(self.skillpoints)+" skill points. \n"+\
                "Type skills to list skills. Leave blank to exit (saving points). \n" +\
                "Type a skill to increase: "
            )

            if s == "":
                break

            if s == 'skills':
                self.showSkills()
                continue

            if s not in self.skills.keys():
                print("that's not a skill")
                continue

            # check to make sure the skill isn't maxed out
            if self.skills[s] < 5:
                # skills above 2 cost 2 to level instead of 1
                if self.skills[s] > 2:
                    if self.skillpoints > 1:
                        self.skills[s] += 1
                        self.skillpoints -= 2
                    else:
                        print("not enough to points level this skill")
                # base case: increment skill and decrement skillpoints
                else:
                    self.skills[s] += 1
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
        ) = (x for x in self.skills.values())

        self.update()

# old character constructor i'm keeping for reference
    # by far the worst part of the code
    # def __init__(self, data, **kwargs):
    #     """Character constructor.

    #     Arguments:
    #         data {dict} -- A dictionary with any number of the attributes for the character.
    #     """

    #     self.data = data
    #     # fails if these aren't initialized o.o
    #     self.leftHand = None
    #     self.rightHand = None

    #     # Pull the name and default value from the defaults dict
    #     for key, value in characterCreationDefaults.items():
    #         # This conditional ladder exists in case character creation gets improperly extended
            
    #         # Check if the input has that attribute,
    #         if key in data:
    #             # data[key] instead of value, because we're indexing the defaults dict in this loop
    #             setattr(self, key, data[key])
    #         # otherwise maybe it's a kwarg,
    #         else:
    #             if key in kwargs:
    #                 setattr(self, key, kwargs[key])
    #             # last ditch effort, maybe it's custom
    #             else:
    #                 setattr(self, key, value)

    #     self.suffix = "'s'" if self.name[-1] == "s" or "x" else "s"
        
    #     # (update needs inventory initialized)
    #     self.inventory = []
    #     # Let update do the rest of the construction
    #     self.update()