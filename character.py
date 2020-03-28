import math
import dmfunctions
import resources
from random import randint

# TODO: simplify constructor:
# class Example:
#     def __init__(self, **kwargs):
#         for name, value in kwargs.iteritems():
#             setattr(self, name, value)
    
# x = Example(strength="7", diplomacy="9")
# x.strength;

class Character:

    def __init__(self,

    # properties
    # clas is intentionally misspelled, blair
    name='NPC', race='human', clas='soldier', faction='sgc',
    
    # stats
    level=1, hitdie=8, hp=8, temphp=0, speed=10,

    # attributes
    strength=10, dexterity=10, constitution=10, intelligence=10, wisdom=10, charisma=10,

    # skills
    acting=0,
    anthropology=0, xenoanthropology=0,
    diplomacy=0,
    medicine=0, vehicles=0, technology=0, xenotechnology=0,
    sleightofhand=0, stealth=0,
    insight=0, perception=0, survival=0, tactics=0,
    athletics=0, acrobatics=0,

    # inspiration
    inspiration=0,

    # slots
    leftHand=None, rightHand=None,
    head=None, body=None, legs=None, belt=None, boots=None, gloves=None, back=None,
    
    # stored levelup info
    attributepoints=0, skillpoints=0
    ):

        # properties
        self.name = name
        self.race = race
        self.clas = clas
        self.faction = faction

        # stats
        self.level = level
        self.hitdie = hitdie
        self.hp = hp
        self.temphp = temphp
        self.speed = speed

        # attributes
        self.strength, self.dexterity, self.constitution = strength, dexterity, constitution
        self.intelligence, self.wisdom, self.charisma = intelligence, wisdom, charisma

        # modifiers
        self.strmod = (self.strength-10)//2
        self.dexmod = (self.dexterity-10)//2
        self.conmod = (self.constitution-10)//2
        self.intmod = (self.intelligence-10)//2
        self.wismod = (self.wisdom-10)//2
        self.chamod = (self.charisma-10)//2

        # skills
        self.acting = acting
        self.anthropology = anthropology
        self.xenoanthropology = xenoanthropology
        self.diplomacy = diplomacy
        self.medicine = medicine
        self.vehicles = vehicles
        self.technology = technology
        self.xenotechnology = xenotechnology
        self.sleightofhand = sleightofhand
        self.stealth = stealth
        self.insight = insight
        self.perception = perception
        self.survival = survival
        self.tactics = tactics
        self.athletics = athletics
        self.acrobatics = acrobatics

        # slots
        self.leftHand, self.rightHand = leftHand, rightHand,
        self.head, self.body, self.legs, self.belt, self.boots, self.gloves, self.back = (
        head, body, legs, belt, boots, gloves, back)

        # inspiration
        self.inspiration = inspiration
        
        # levelup info
        self.attributepoints= attributepoints
        self.skillpoints = skillpoints

        # lists
        self.inventory = []
        self.gear = [self.leftHand, self.rightHand, self.head, self.body, self.legs, self.belt, self.boots, self.gloves, self.back]
        self.armor = [self.head, self.body, self.legs, self.belt, self.boots, self.gloves, self.back]
        self.attributes = [self.strength, self.dexterity, self.constitution, self.intelligence, self.wisdom, self.charisma]
        self.skills = [self.acting, self.anthropology, self.xenoanthropology, self.diplomacy,
            self.medicine, self.vehicles, self.technology, self.xenotechnology, self.sleightofhand, self.stealth,
            self.insight, self.perception, self.survival, self.tactics, self.athletics, self.acrobatics]
        self.feats = []

        # character data

        self.gearweight = 0.0
        for item in self.gear and self.inventory:
            try:
                    gearweight += item.weight
            except: pass

            # TODO recursive function to calculate gear weight from nested items
            try:  
                for storeditem in item.storage:
                    gearweight += storeditem.weight
            except: pass

        self.armorAC = 0
        for item in self.armor:
            try:
                armorAC += item.bonusAC
            except: pass
        # AC is floor 6 instead of 10 because 3d6 rolls are far less likely to overcome high ACs,
        # and this system has lots of high ACs due to armor slots
        self.AC = 6 + self.dexmod + self.armorAC
        self.maxhp = (self.hitdie + self.conmod) + (self.level - 1) * (self.conmod)

    def equip(self, item, slot):
        '''slot is a (camel)case-sensitive string'''

        if slot in resources.slots:
            if self.gear[resources.slots.index(slot)] == None:
                self.gear[resources.slots.index(slot)] = item

        self.leftHand, self.rightHand, self.head, self.body, self.legs, self.belt, self.boots, self.gloves, self.back = (x for x in self.gear)
        self.update()       

    def unequip(self, item, slot):
        '''slot is a (camel)case-sensitive string'''

        # resources.slots is an identical slots list with strings instead of variables
        if slot in resources.slots:
            if self.gear[resources.slots.index(slot)] != None:
                self.inventory.append(self.gear[resources.slots.index(slot)])
                self.gear[resources.slots.index(slot)] = None

        self.leftHand, self.rightHand, self.head, self.body, self.legs, self.belt, self.boots, self.gloves, self.back = (x for x in self.gear)
        self.update()

    def grab(self, item, hand=None):

        if hand == None:
            if self.rightHand != None:
                self.rightHand = item
            elif self.leftHand != None:
                self.leftHand = item
            else:
                print('ope')
                
        if hand == 'right':
            if self.rightHand != None:
                self.rightHand = item
            else:
                print('ope')

        if hand == 'left':
            if self.leftHand != None:
                self.leftHand = item
            else:
                print('ope')

        self.update()

    def stow(self, item, storageItem=None):
        if storageItem == None:
            self.inventory.append(item)
        else:
            storageItem.storage.append(item)

    def showInventory(self):
        for item in self.inventory:
            print('    ' + item.name)
            dmfunctions.printcontents(item)

    def showGear(self):
        for item in self.gear:
            print(item.name)
            dmfunctions.printcontents(item)

    def showAttributes(self):
        for attribute in resources.attributes:
            print(attribute + ': ' + str(eval('self.' + attribute)))

    def showSkills(self):
        for skill in resources.skills:
           print(skill + ": " + str(eval('self.' + skill)))

    def show(self):
        if self.name[-1] == 's':
            suffix = "'"
        else:
            suffix = "'s"

        print(self.name + ' is a level ' + str(self.level) + ' ' + self.race + ' ' + self.clas + '.')
        print(self.name + ' has ' + str(self.hp) + ' health, ' + str(self.temphp) + ' temp health, and ' + str(self.maxhp) + ' max health.')
        print(self.name + suffix + ' attributes are: ')
        for attribute in resources.attributes:
            print('    ' + attribute + ': ' + str(eval('self.' + attribute)))
        # skills
        print(self.name + suffix + ' skills are:')
        for skill in resources.skills:
            print('    ' + skill + ': ' + str(eval('self.' + skill)))
        print(self.name + ' has an AC of ' + str(self.AC) + ' and is wearing: ')
        for slot in resources.slots:
            try:
                print('    ' + slot + ': ' + eval('self.' + slot).name)
            except:
                print('    ' + slot + ': None')
        print(self.name + suffix + ' inventory:')
        self.showInventory()
        print(self.name + ' has ' + str(self.inspiration) + ' inspiration points, ' + str(self.attributepoints) + ' attribute points, and ' + str(self.skillpoints) + ' skill points.')

    def initiative(self, dice=3, die=6):
        return sum([randint(1,die) for x in range(dice)]) + self.dexmod

    def update(self):
        self.strmod = (self.strength-10)//2
        self.dexmod = (self.dexterity-10)//2
        self.conmod = (self.constitution-10)//2
        self.intmod = (self.intelligence-10)//2
        self.wismod = (self.wisdom-10)//2
        self.chamod = (self.charisma-10)//2

        self.gear = [self.leftHand, self.rightHand, self.head, self.body, self.legs, self.belt, self.boots, self.gloves, self.back]
        self.gearweight = 0.0
        for item in self.gear and self.inventory:
            try:
                self.gearweight += item.weight
            except: pass
        self.gearweight = round(self.gearweight, 2)

        self.armor = [self.head, self.body, self.legs, self.belt, self.boots, self.gloves, self.back]
        self.armorAC = 0
        for item in self.armor:
            try:
                armorAC += item.bonusAC
            except: pass

        self.AC = 6 + self.dexmod + self.armorAC

        self.attributes = [self.strength, self.dexterity, self.constitution, self.intelligence, self.wisdom, self.charisma]
        self.skills = [self.acting, self.anthropology, self.xenoanthropology, self.diplomacy,
            self.medicine, self.vehicles, self.technology, self.xenotechnology, self.sleightofhand, self.stealth,
            self.insight, self.perception, self.survival, self.tactics, self.athletics, self.acrobatics]

        # hp = hitdie+mod for level 1, add smaller bonus for each level
        # standard 5e formula is:
        # self.hp = (self.hitdie + self.conmod) + (self.level - 1) * (self.hitdie // 2 + 1 + self.conmod)
        self.maxhp = (self.hitdie + self.conmod) + (self.level - 1) * (self.conmod)

    def randomizeAttributes(self):

        self.strength, self.dexterity, self.constitution, self.intelligence, self.wisdom, self.charisma = (
            sum(sorted([randint(1,6) for x in range(4)])[1:]) for x in self.attributes)

        self.update()

    def pointBuyAttributes(self, points=27):

        self.strength, self.dexterity, self.constitution, self.intelligence, self.wisdom, self.charisma = (8 for x in self.attributes)
        self.update()

        while points > 0:

            s = input('type an attribute to += 1: ')
            if self.attributes[resources.attributes.index(s)] >= 15:
                self.attributes[resources.attributes.index(s)] += 1

                if self.attributes[resources.attributes.index(s)] > 13:
                    points -= 2
                else:
                    points -= 1
            else:
                print('attribute at starting cap (15)')

    def levelUp(self):

        self.level += 1

        # level attributes
        self.attributepoints += 1
        print('current attributes: strength ' + str(self.strength) + ', dexterity ' + str(self.dexterity) + ', constitution ' + str(self.constitution)
        + ', intelligence ' + str(self.intelligence) + ', wisdom ' + str(self.wisdom) + ', charisma ' + str(self.charisma))

        while self.attributepoints > 0:
            s = input('type an attribute (or leave blank to exit) to increase by 1: ')

            if s == '':
                break

            if self.attributes[resources.attributes.index(s)] < 20:
                self.attributes[resources.attributes.index(s)] += 1
                self.attributepoints -= 1
            else:
                print('attribute maxed; pick a different attribute')
                self.attributepoints += 1

        # update attributes from new list
        self.strength, self.dexterity, self.constitution, self.intelligence, self.wisdom, self.charisma = (x for x in self.attributes)

        # update character now in case int is increased enough to effect skillpoints
        self.update()

        # levelup skills
        self.skillpoints += 3 + self.intmod

        while self.skillpoints > 0:
            s = input('type a skill (or leave blank to exit) to increase by 1: ')

            if s == '':
                break
            # resources.skills is a copy of self.skills with strings instead of variables;
            # self.skills[resources.skills.index(s)] selects the appropriate skill via user input
            if s not in resources.skills:
                print('that is not a skill')
            
            # check to make sure the skill isn't maxed out
            elif self.skills[resources.skills.index(s)] < 5:
                # skills above 2 cost 2 to level instead of 1
                if self.skills[resources.skills.index(s)] > 2:
                    if self.skillpoints > 1:
                        self.skills[resources.skills.index(s)] += 1
                        self.skillpoints -= 2
                    else:
                        print('not enough to points level this skill')
                # base case: increment skill and decrement skillpoints
                else:
                    self.skills[resources.skills.index(s)] += 1
                    self.skillpoints -= 1
            else:
                print('skill maxed; pick a different skill')

        
        (self.acting, self.anthropology, self.xenoanthropology, self.diplomacy,
        self.medicine, self.vehicles, self.technology, self.xenotechnology, self.sleightofhand, self.stealth,
        self.insight, self.perception, self.survival, self.tactics, self.athletics, self.acrobatics) = (x for x in self.skills)

        # update character again
        self.update()
