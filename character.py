# pylint: disable=no-member
# pylint: disable=access-member-before-definition
# (pylint doesn't like the constructor's update shortcut)

from random import randint

characterCreationDefaults = {
    # basic information                  v (intentionally misspelt)
    "name": "NPC", "race": "human", "clas": "soldier", "faction": "sgc",
    # stats
    "level": 1, "hitdie": 8, "hp": 8, "temphp": 0, "speed": 10,
    # attributes
    "strength": 10, "dexterity": 10, "constitution": 10, "intelligence": 10, "wisdom": 10, "charisma": 10,
    # skills
    "acting": 0, "anthropology": 0, "xenoanthropology": 0, "sleightofhand": 0, "stealth": 0, "diplomacy": 0, "medicine": 0, "vehicles": 0,
    "xenotechnology": 0, "technology": 0, "insight": 0, "perception": 0, "survival": 0, "tactics": 0, "athletics": 0, "acrobatics": 0,
    # hands
    "leftHand": None, "rightHand": None,
    # gear
    "head": None, "chest": None, "legs": None, "belt": None, "boots": None, "gloves": None, "back": None,
    # levelup info
    "attributepoints": 0, "skillpoints": 0,
    # inspiration
    "inspiration": 0
}


class Character:
    """Generic character class. Construct with data, an {attrname: value} dict.
    Optionally construct with an unpacked *dict.
    """

    def __init__(self, data, **kwargs):

        for key, value in characterCreationDefaults.items():
            if key not in data: # * (see EOF)
                setattr(self, key, value)
            else:
                setattr(self, key, data[key])

        for key in kwargs:
            setattr(self, key, kwargs[key])

        self.suffix = "'" if self.name[-1] == ("s" or "x") else "'s"
        self.inventory = []
        # update builds lists like self.gear, self.attributes, etc
        self.update()

    def getJSON(self):
        """Creates and returns a (JSON serializable) dict of the character.

        Returns:
            dict -- A dictionary version of the character's attributes.
        """
        return {key:getattr(self,key) for key in characterCreationDefaults}

    def update(self):
        """Updates and recalculates various attributes of the character.
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

        # character data
        self.gearweight = 0.0
        for item in list(self.gear.values()) + self.inventory:
            if hasattr(item, "weight"):
                self.gearweight += item.getWeight()

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

        if slot[:4] == "left":
            slot = "leftHand"
        if slot[:5] == "right":
            slot = "rightHand"

        if slot in self.gear and getattr(self, slot) is None:
            setattr(self, slot, item)
        else:
            print("invalid equip slot")

        self.update()

    def unequip(self, slot):
        """Un-equips the provided item from the slot.

        Arguments:
            slot {str} -- The slot to un-equip from.
        """
        slot = slot.lower().strip()

        if slot[:4] == "left":
            slot = "leftHand"
        if slot[:5] == "right":
            slot = "rightHand"

        if slot in self.gear and getattr(self, slot) is not None:
            self.inventory.append(getattr(self, slot))
            setattr(self, slot, None)
        else:
            print("invalid unequip slot")

        self.update()

    def heal(self, h=None):
        """Heals the character for h health.

        Args:
            h (int, optional): Hitpoints to heal; leave blank to full heal. Defaults to None.
        """
        # if we're doing a basic full heal...
        if h == None:
            self.hp = self.maxhp
        # else, make sure we won't go over max health
        elif self.hp + h > self.maxhp:
            self.hp = self.maxhp
        # otherwise, just add the hp
        else:
            self.hp += h

    def hurt(self, d):
        """Hurts the character for d damage.

        Args:
            d (int): damage to deal
        """
        if d > self.temphp:
            d -= self.temphp
            self.temphp = 0
            self.hp -= d
        else:
            self.temphp -= d
            

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
        print("Inventory:")
        for item in self.inventory:
            print(item.name)
            item.show()

    def showGear(self):
        """Prints the character's gear.
        """
        print(f"{self.name}{self.suffix} AC is {self.AC} and is wearing:")
        for slot, item in self.gear.items():
            print(f"{slot}: {item}")
            if item is not None:
                item.show(spacing='    ')
        print("")

    def showAttributes(self):
        """Prints the attributes of the character.
        """
        print(self.name + self.suffix + " attributes are:")
        for name, attribute in self.attributes.items():
            print(f"{name}: {attribute}")
        print("")

    def showSkills(self):
        """Prints the skills of the character.
        """
        print(self.name + self.suffix + " skills are:")
        for name, skill in self.skills.items():
            print(f"{name}: {skill}")
        print("")

    def show(self):
        """Prints the current status of the character.
        """

        print(f"{self.name} is a level {self.level} {self.race} {self.clas}.")
        print(f"{self.name} has {self.hp} health, {self.temphp} temp health, and {self.maxhp} max health.")

        self.showAttributes()
        self.showSkills()
        self.showGear()
        self.showInventory()

        print(f"{self.name} has {self.inspiration} inspiration points, " + \
        f"{self.attributepoints} attribute points, and {self.skillpoints} skill points.")

    def initiative(self, dice=3, die=6):
        """Rolls initiative for the character.

        Keyword Arguments:
            dice {int} -- The number of dice to roll. (default: {3})
            die {int} -- The number of sides each die should have. (default: {6})

        Returns:
            int -- The initiative roll.
        """
        return sum([randint(1, die) for x in range(dice)]) + self.dexmod

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

    # everything below is from 2019. it's pretty sloppy and largely deprecated
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

        self.showAttributes()

        while points > 0:

            s = bug_player()

            # s is only False when you put in a bad attribute
            if not s:
                continue
            if is_stalled():
                break

            if self.attributes[s] < 15:
                if self.attributes[s] < 13:
                    points -= 1
                    self.attributes[s] += 1
                    print(f'Attribute {s} increased by 1. {points} points remaining.')
                elif points > 1:
                    points -= 2
                    self.attributes[s] += 1
                else:
                    print(f'Not enough points to level {s}. {points} points remaining.')
            else:
                print(f"attribute {s} at starting cap (15)")


    def levelUp(self):
        """Levels up the character.
        """
        self.level += 1

        # level attributes
        if  self.level % 4 == 0:
            self.attributepoints += 2
            print(
                f"current attributes: {self.strength} strength, {self.dexterity} dexterity, \
                {self.constitution} constitution, {self.intelligence} intelligence, \
                {self.wisdom} wisdom, {self.charisma} charisma"
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

        self.showSkills()
        while self.skillpoints > 0:
            s = input(
                f"You have {self.skillpoints} skill points. \n"+\
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

# *
# setdefault benched at 5s/million iterations,
# checking membership benched at 4.5s/million