from random import randint
from copy import deepcopy
import races
import classes

# this dict only really gets used in character creation and 
defaults = {
    # biographical information           v (intentionally misspelt)
    "name": "NPC", "race": "human", "clas": "soldier", "faction": "",

    # stats                             (m/s)
    "level": 1, "hp": 10, "tempHp": 0, "speed": 10.0,

    "attributes": {
        "strength": 8, "dexterity": 8, "constitution": 8, "intelligence": 8, "wisdom": 8, "charisma": 8
    },

    "skills": {
        "acting": 0, "anthropology": 0, "xenoanthropology": 0, "sleightofhand": 0, "stealth": 0,
        "diplomacy": 0, "medicine": 0, "vehicles": 0, "xenotechnology": 0, "technology": 0,
        "insight": 0, "perception": 0, "survival": 0, "tactics": 0, "athletics": 0, "acrobatics": 0
    },

    "slots": {
        "leftHand": None, "rightHand": None, # hands are aliased as "left" or "right"
        "head": None, "chest": None, "legs": None, "belt": None, "boots": None, "gloves": None, "back": None,
    },

    # levelup info
    "attributePoints": 0, "skillPoints": 0,
    # inspiration
    "inspiration": 0
}

# a note about the word attribute:
# most ttrpg systems i've used use "attribute" to refer to innate stat values like strength or wisdom
# unfortunately, python object members are called attributes too. so there's some name collision i've tried to mitigate
# this brings me to a potential TODO: combine the skills and attributes dicts (& bonuses) into a stats dict
class Character:
    """Generic character class. Construct with an unpacked **dict.
    """
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self,key,value)

    @classmethod
    def new(cls, **kwargs):
        """uncontrolled factory method for first-time character creation.
        using this to load character jsons will run unnecessary recalculation overhead

        Returns:
            character: created
        """
        charObj = cls(**(defaults | kwargs))

        charObj.suffix = "'" if charObj.name[-1] == ("s" or "x") else "'s"

        charObj.updateBonuses()
        # race/class is done between bonuses and mods because it
        # requires bonuses to exist, and it affects modifier calculation
        charObj.updateRaceAndClass()
        charObj.updateMods()
        # AC and MaxHp depend on mods
        charObj.updateAC()
        charObj.updateMaxHp()
        charObj.updateWeight()
        # speed depends on weight
        charObj.updateSpeed()

        return charObj

    def getJSON(self):
        """Creates and returns a (JSON serializable, writeable) dict of the character.

        Returns:
            dict -- of the character's attributes.
        """
        attrs = vars(self)
        # item.getJSON does recursion
        attrs['slots'] = {slot:item.getJSON() if item else None for slot,item in self.slots.items()}
        return attrs

    #############################
    #### stat update methods ####
    #############################

    def updateRaceAndClass(self, race=False, clas=False):
        # i decided functions were the simplest way to execute race and class modifiers
        if not hasattr(self,'raceAndClassApplied'):
            races.__dict__[race.replace("'","") if race else self.race.replace("'","")](self)
            classes.__dict__[clas if clas else self.clas](self)
            self.raceAndClassApplied=True

    def updateBonuses(self):
        self.bonusAttrs = {attrName:sum(
            item.bonusAttrs.get(attrName,0) if item else 0 for item in self.slots.values()
            ) for attrName in self.attributes}
        self.bonusSkills = {skillName:sum(
            item.bonusSkills.get(skillName,0) if item else 0 for item in self.slots.values()
            ) for skillName in self.skills}

    def updateMods(self):
        self.attrMods = {attrName:(self.attributes[attrName] + self.bonusAttrs[attrName] - 10) // 2 \
            for attrName in self.attributes}

    def updateAC(self):
        # hasattr ternary sneakily also checks if the item isn't None
        self.armorAC = sum(item.bonusAC if hasattr(item,'bonusAC') else 0 for item in self.slots.values())
        self.AC = 6 + self.armorAC + self.attrMods['dexterity']

    def updateMaxHp(self):
        # hp = hitDie+mod for level 1, conMod for each other level
        # standard 5e formula is:
        # hp = (hitDie + conMod) + (level - 1) * (hitDie // 2 + 1 + conMod)
        try:
            self.maxHp = (self.hitDie + self.attrMods['constitution']) + ((self.level - 1) * self.attrMods['constitution'])
        except AttributeError:
            print("you used the normal character constructor with the defaults dict instead of the factory method again")

    def updateWeight(self):
        # getWeight() does nested item recursion
        self.gearWeight = sum(item.getWeight() if item else 0 for item in self.slots.values())

    def updateSpeed(self):
        # 1.5 and 100 just felt right for the speed formula after trying different values
        self.speed = 10.0 - self.gearWeight**1.5//100 # breakpoints at 21kg, 34, 44, 54...(100*n)**(2/3)kg
        if self.speed < 1: # ultimately i don't want to stop people from being able to like, crawl
            self.speed = 1

    def update(self):
        """debug tool that builds all character meta variables
        """
        self.updateRaceAndClass()
        self.updateBonuses()
        self.updateMods()
        self.updateAC()
        self.updateMaxHp()
        self.updateWeight()
        self.updateSpeed()
        self.suffix = "'" if self.name[-1] == ("s" or "x") else "'s"

    # TODO P2: this needs more testing
    def handleNewItem(self, item, don=True):
        """updates meta-variables whenever a new item is equipped or unequipped

        Args:
            item (item): to handle
            don (bool, optional): True if equipping (donning). Defaults to True.
        """
        don = 1 if don else -1

        self.gearWeight += item.getWeight() * don
        self.updateSpeed()

        if hasattr(item,'bonusAC'):
            self.armorAC += item.bonusAC * don

        for skillName,skillValue in item.bonusSkills.items():
            self.bonusSkills[skillName] += skillValue * don

        for attrName,attrValue in item.bonusAttrs.items():
            self.bonusAttrs[attrName] += attrValue * don
            self.attrMods[attrName] = (self.attributes[attr] + self.bonusAttrs[attr] - 10) // 2
            if attrName == 'dexterity':
                self.AC = 6 + self.armorAC + self.attrMods['dexterity']
            if attrName == 'constitution':
                self.maxHp = (self.hitDie + self.attrMods['constitution']) + \
                ((self.level - 1) * self.attrMods['constitution'])

    #############################
    # character item handling
    #############################
    def handleSlotInput(slot):
        slot = slot.strip().lower()
        if slot[:4] == "left" or slot[:2] == "lh":
            slot = "leftHand"
        if slot[:5] == "right" or slot[:2] == "rh":
            slot = "rightHand"
        return slot

    def equip(self, item, slot):
        """moves an item to a character object's slot.

        Arguments:
            item {str} -- to equip
            slot {str} -- to move to
        """
        slot = handleSlotInput(slot)

        if slot in self.slots:
            if self.slots[slot] is None:
                # the actual equip function, everything else is just boilerplate
                self.slots[slot] = item
                self.handleNewItem(item, don=True)

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
        slot = handleSlotInput(slot)
        item = self.slots[slot]

        if item.store(container):
            self.handleNewItem(item, don=False)
            # remove item
            self.slots[slot] = None


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
        for name in self.attributes:
            print(f"    {name}: {self.attributes[name]+self.bonusAttrs[name]}")

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
        print(f"{self.name} has {self.hp} health, {self.tempHp} temp health, and {self.maxHp} max health.")

        self.showAttributes()
        self.showSkills()
        self.showSlots()

        print(f"{self.name} has {self.inspiration} inspiration points, " + \
        f"{self.attributePoints} attribute points, and {self.skillPoints} skill points.")

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
        return sum(randint(1, die) for x in range(dice)) + self.attrMods['dexterity']

    def heal(self, h=None):
        """Heals the character for h health.

        Args:
            h (int, optional): Hitpoints to heal; leave blank to full heal. Defaults to None.
        """
        # if we're doing a basic full heal...
        if h == None:
            self.hp = self.maxHp
        else:
            self.hp += h
        # (don't overheal)
        if self.hp > self.maxHp:
            self.hp = self.maxHp

    def hurt(self, d):
        """Hurts the character for d damage.

        Args:
            d (int): damage to deal
        """
        if d > self.tempHp:
            d -= self.tempHp
            self.tempHp = 0
            self.hp -= d
        else:
            self.tempHp -= d

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
             for name in self.attributes}

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
        charCopy.attributes = {attr:8 for attr in self.attributes}

        def bug_player():
            s = input("type an attribute to increment: ").lower()
            if s not in charCopy.attributes.keys():
                print("invalid attribute. attributes are: " + str(list(charCopy.attributes.keys())))
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


    # TODO P1: update this for the new defaults dict
    def levelUp(self):
        """Levels up the character.
        """
        charCopy = deepcopy(self)
        charCopy.level += 1

        # level attributes
        if  charCopy.level % 4 == 0:
            charCopy.attributePoints += 2
            charCopy.showAttributes()

        while charCopy.attributePoints > 0:
            s = input("type an attribute (or leave blank to exit) to increase by 1: ").lower()

            if s == "":
                break

            if s not in charCopy.attributes:
                print("invalid attribute. attributes are:",*list(charCopy.attributes.keys()))

            if charCopy.attributes[s] < 20:
                charCopy.attributes[s] += 1
                charCopy.attributePoints -= 1
            else:
                print("attribute maxed; pick a different attribute")
                charCopy.attributePoints += 1

        # update. int may have been increased enough to effect skillPoints
        charCopy.update()

        # levelup skills
        charCopy.skillPoints += 3 + charCopy.attrMods['intelligence']

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
# these 2 dense dictcomps are collapsed from this code:
# self.bonusAttrs = {attrName:0 for attrName in self.attributes}
# self.bonusSkills = {skillName:0 for skillName in self.skills}
# for item in self.slots.values():
#     if item:
#         for statName,statValue in item.bonusAttrs.items():
#             self.bonusAttrs[statName] += statValue
#         for statName,statValue in item.bonusSkills.items():
#             self.bonusSkills[statName] += statValue