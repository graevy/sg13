class Item:
    def __init__(self, name, description=None, weight=0, storage=[]):
        self.name = name
        self.description = description
        self.weight = weight
        self.storage = storage

    def __str__(self):
        return self.name

    def show(self):
        print(self.name+" storage:")
        def recur(item):
            for thing in item:
                print(thing.name)
                if thing.storage != []:
                    thing.recur()

        recur(self)


class Weapon(Item):
    def __init__(self, name, description=None, weight=0.0, storage=[], \
    range=3, damage=8, proficiency='strength', proficiencytype='melee', cqcpenalty=0):

        # sooo much cleaner
        super().__init__(name, description=None, weight=0.0, storage=[])

        self.range, self.damage, self.proficiency, self.proficiencytype, self.cqcpenalty = \
        range, damage, proficiency, proficiencytype, cqcpenalty

    # if i ever go for weapon realism this needs to get done
    def reload(self):
        # TODO
        pass

class Armor(Item):
    def __init__(self, name, description=None, weight=0.0, storage=[], bonusAC=0):

        super().__init__(name, description=None, weight=0.0, storage=[])
        self.bonusAC = bonusAC

##################################
#############Old classes#############
##################################

# class Weapon(Item):
#     def __init__(
#         self,
#         name,
#         description=None,
#         weight=0.0,
#         range=3,
#         damage=8,
#         proficiency="strength",
#         proficiencytype="melee",
#         cqcpenalty=0,
#         storage=[],
#     ):
#         Item.__init__(self, name, description=None, weight=0.0, storage=[])
#         self.range = range
#         self.damage = damage
#         self.proficiency = proficiency
#         self.proficiencytype = proficiencytype
#         self.cqcpenalty = cqcpenalty


# class Armor(Item):
#     def __init__(self, name, description=None, weight=0.0, bonusAC=0, storage=[]):
        
#         Item.__init__(self, name, description=None, weight=0.0, storage=[])
#         self.bonusAC = bonusAC