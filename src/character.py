# pylint: disable=no-member
# pylint: disable=access-member-before-definition
# (pylint doesn't like the constructor's update shortcut)

from random import randint
from copy import deepcopy

characterCreationDefaults = {
    # biographical information           v (intentionally misspelt)
    "name": "NPC", "race": "human", "clas": "soldier", "faction": "",

    # stats                                          m/s
    "level": 1, "hitdie": 8, "hp": 8, "temphp": 0, "speed": 10,

    "attributes": {
    "strength": 10, "dexterity": 10, "constitution": 10, "intelligence": 10, "wisdom": 10, "charisma": 10
    },

    "skills": {
    "acting": 0, "anthropology": 0, "xenoanthropology": 0, "sleightofhand": 0, "stealth": 0, "diplomacy": 0, "medicine": 0, "vehicles": 0,
    "xenotechnology": 0, "technology": 0, "insight": 0, "perception": 0, "survival": 0, "tactics": 0, "athletics": 0, "acrobatics": 0
    },

    "slots": {
    "leftHand": None, "rightHand": None, # hands are aliased as "left" or "right"
    "head": None, "chest": None, "legs": None, "belt": None, "boots": None, "gloves": None, "back": None,
    },

    # levelup info
    "attributepoints": 0, "skillpoints": 0,
    # inspiration
    "inspiration": 0
}


class Character:
    """Generic character class. Construct with attrs, an {attrname: value} dict.
    Optionally construct with an unpacked *dict.
    """

    def __init__(self, attrs, **kwargs):
        for key, value in characterCreationDefaults.items():
            if key not in attrs: # *
                setattr(self, key, value)
            else:
                setattr(self, key, attrs[key])

        for key in kwargs:
            setattr(self, key, kwargs[key])

        self.suffix = "'" if self.name[-1] == ("s" or "x") else "'s"
        # update recalculates metavars
        self.update()

    def getJSON(self):
        """Creates and returns a (JSON serializable) dict of the character.

        Returns:
            dict -- A dictionary version of the character's attributes.
        """
        attrs = vars(self)
        # item.getJSON already does recursion
        attrs['slots'] = {slot:item.getJSON() if item else None for slot,item in self.slots.items()}
        return attrs

    def update(self):
        """Updates and recalculates various attributes of the character.
        """
        self.strMod = (self.attributes['strength'] - 10) // 2
        self.dexMod = (self.attributes['dexterity'] - 10) // 2
        self.conMod = (self.attributes['constitution'] - 10) // 2
        self.intMod = (self.attributes['intelligence'] - 10) // 2
        self.wisMod = (self.attributes['wisdom'] - 10) // 2
        self.chaMod = (self.attributes['charisma'] - 10) // 2

        # character data
        self.gearWeight = sum([item.getWeight() if item else 0 for item in self.slots.values()])
        self.speed = 10 - self.gearWeight**1.5//150 # breakpoints at 29kg, 45, 59, 72...(150*n)**(2/3)kg
        if self.speed < 1:
            self.speed = 1

        self.armorAC = sum([item.bonusAC if hasattr(item,'bonusAC') else 0 for item in self.slots.values()])
        self.AC = 6 + self.armorAC + self.dexMod

        # hp = hitdie+mod for level 1, conMod for each other level
        # standard 5e formula is:
        # self.hp = (self.hitdie + self.conMod) + (self.level - 1) * (self.hitdie // 2 + 1 + self.conMod)
        self.maxhp = (self.hitdie + self.conMod) + ((self.level - 1) * self.conMod)

    #############################
    # character item handling
    #############################
    def equip(self, item, slot):
        """moves an item to a character object's slot.

        Arguments:
            item {str} -- to equip
            slot {str} -- to move to
        """
        slot = slot.strip().lower()
        if slot[:4] == "left":
            slot = "leftHand"
        if slot[:5] == "right":
            slot = "rightHand"

        if slot in self.slots:
            if self.slots[slot] is None:
                self.slots[slot] = item
            else:
                print(f"{slot} already contains {self.slots[slot]}")
        else:
            print(f"{slot} invalid. valid slots are:\n" +
                "leftHand, rightHand, head, chest, legs, belt, boots, gloves, back")

        self.update()
    
    # TODO P1: implement
    def stow(self, slot, container):
        """Stores a character object's slot's item in another item.

        Arguments:
            item {Object} -- to store.

        Keyword Arguments:
            container {Object} -- to store in.
        """
        slot = slot.strip().lower()
        if slot[:4] == "left":
            slot = "leftHand"
        if slot[:5] == "right":
            slot = "rightHand"

        # container.storage.append(item)

        self.update()
    
    #############################
    # character pretty printing
    #############################
    def showSlots(self):
        """Prints the character's slot contents.
        """
        print(f"{self.name}{self.suffix} AC is {self.AC} and is wearing:")
        for slot, item in self.slots.items():
            print(f"    {slot}: {item}")
            if item is not None:
                item.show(spacing='        ')
        print("")

    def showAttributes(self):
        """Prints the attributes of the character.
        """
        print(self.name + self.suffix + " attributes are:")
        for name, attribute in self.attributes.items():
            print(f"    {name}: {attribute}")

    def showSkills(self):
        """Prints the skills of the character.
        """
        print(self.name + self.suffix + " skills are:")
        for name, skill in self.skills.items():
            print(f"    {name}: {skill}")

    def show(self):
        """Prints the current status of the character.
        """

        print(f"{self.name} is a level {self.level} {self.race} {self.clas}.")
        print(f"{self.name} has {self.hp} health, {self.temphp} temp health, and {self.maxhp} max health.")

        self.showAttributes()
        self.showSkills()
        self.showSlots()

        print(f"{self.name} has {self.inspiration} inspiration points, " + \
        f"{self.attributepoints} attribute points, and {self.skillpoints} skill points.")

    #############################
    #     character combat
    #############################
    def initiative(self, dice=3, die=6):
        """Rolls initiative for the character.

        Keyword Arguments:
            dice {int} -- The number of dice to roll. (default: {3})
            die {int} -- The number of sides each die should have. (default: {6})

        Returns:
            int -- The initiative roll.
        """
        return sum([randint(1, die) for x in range(dice)]) + self.dexMod

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

    #############################
    # character leveling
    #############################
    def randomizeAttributes(self):
        """Randomizes character attributes. 4d6 minus lowest roll per attribute
        """
        self.attributes = {name:
        sum(
            sorted(
                [randint(1,6) for x in range(4)]
                )[1:]
            )
             for name,stat in self.attributes.items()}

        self.update()

    # everything below is from 2019. it's smelly and largely deprecated. recently updated some of it
    def pointBuyAttributes(self, points=27):
        """Starts the point buy process for the character.

        Keyword Arguments:
            points {int} -- The number of points to use in the pointbuy. (default: {27})
        """
        # wrap everything in a copy for aborts
        charCopy = deepcopy(self)
        # set all ability scores to 8
        charCopy.attributes = {attr:8 for attr,stat in self.attributes.items()}

        def bug_player():
            s = input("type an attribute to increment: ").lower()
            if s not in charCopy.attributes.keys():
                print("invalid attribute. attributes are: " + str(charCopy.attributes.keys())[11:-2])
                return False
            return s

        # it's possible in some point totals to have all attributes above 12 and still have 1 point left;
        # buying any more attributes becomes impossible
        def is_stalled():
            if points != 1:
                return False
            for attribute in charCopy.attributes.values():
                if attribute < 13:
                    return False
            return True

        charCopy.showAttributes()

        while points > 0:

            s = bug_player()

            # s is only False when you put in a bad attribute
            if not s:
                continue
            if is_stalled():
                break

            if charCopy.attributes[s] < 15:
                if charCopy.attributes[s] < 13:
                    points -= 1
                    charCopy.attributes[s] += 1
                    print(f'Attribute {s} increased by 1. {points} points remaining.')
                elif points > 1:
                    points -= 2
                    charCopy.attributes[s] += 1
                else:
                    print(f'Not enough points to level {s}. {points} points remaining.')
            else:
                print(f"attribute {s} at starting cap (15)")

        self = charCopy


    # TODO: update this for the new defaults dict
    def levelUp(self):
        """Levels up the character.
        """
        charCopy = deepcopy(self)
        charCopy.level += 1

        # level attributes
        if  charCopy.level % 4 == 0:
            charCopy.attributepoints += 2
            print(
                f"current attributes: {charCopy.strength} strength, {charCopy.dexterity} dexterity, \
                {charCopy.constitution} constitution, {charCopy.intelligence} intelligence, \
                {charCopy.wisdom} wisdom, {charCopy.charisma} charisma"
                )

        while charCopy.attributepoints > 0:
            s = input("type an attribute (or leave blank to exit) to increase by 1: ").lower()

            if s == "":
                break

            if s not in charCopy.attributes:
                print("invalid attribute. attributes are: " + str(charCopy.attributes.keys())[11:-2])

            if charCopy.attributes[s] < 20:
                charCopy.attributes[s] += 1
                charCopy.attributepoints -= 1
            else:
                print("attribute maxed; pick a different attribute")
                charCopy.attributepoints += 1

        # update intMod. int may have been increased enough to effect skillPoints
        charCopy.intMod = (charCopy.attributes['intelligence'] - 10) // 2

        # levelup skills
        charCopy.skillPoints += 3 + charCopy.intMod

        charCopy.showSkills()
        while charCopy.skillPoints > 0:
            s = input(
                f"You have {charCopy.skillPoints} skill points. \n"+\
                "Type skills to list skills. Leave blank to exit (saving points). \n" +\
                "Type a skill to increase: "
            )

            if s == "":
                break

            if s == 'skills':
                charCopy.showSkills()
                continue

            if s not in charCopy.skills:
                print("that's not a skill")
                continue

            # check to make sure the skill isn't maxed out
            if charCopy.skills[s] < 5:
                # skills above 2 cost 2 to level instead of 1
                if charCopy.skills[s] > 2:
                    if charCopy.skillPoints > 1:
                        charCopy.skills[s] += 1
                        charCopy.skillPoints -= 2
                    else:
                        print("not enough to points level this skill")
                # base case: increment skill and decrement skillPoints
                else:
                    charCopy.skills[s] += 1
                    charCopy.skillPoints -= 1
            else:
                print("skill maxed; pick a different skill")

        charCopy.update()
        self = charCopy

# *
# setdefault benched at 5s/million iterations,
# checking membership benched at 4.5s/million
