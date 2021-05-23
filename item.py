class Item:
    def __init__(self, name, description=None, weight=0, storage=[]):
        self.name = name
        self.description = description
        self.weight = weight
        self.storage = storage

    def __str__(self):
        return self.name

    def getStorage(self):
        return self.storage

    def show(self):
        print(self.name+" storage:")
        def recur(item):
            for thing in item:
                print(thing.name)
                if thing.storage != []:
                    thing.recur()

        recur(self)


class Weapon(Item):
    def __init__(
        self,
        name,
        description=None,
        weight=0.0,
        range=3,
        damage=8,
        proficiency="strength",
        proficiencytype="melee",
        cqcpenalty=0,
        storage=[],
    ):
        Item.__init__(self, name, description=None, weight=0.0, storage=[])
        self.range = range
        self.damage = damage
        self.proficiency = proficiency
        self.proficiencytype = proficiencytype
        self.cqcpenalty = cqcpenalty

    def getProficiency(self):
        return self.proficiency

    def getProficiencyType(self):
        return self.proficiencytype

    def reload(self):
        # TODO
        pass


class Armor(Item):
    def __init__(self, name, description=None, weight=0.0, bonusAC=0, storage=[]):
        
        Item.__init__(self, name, description=None, weight=0.0, storage=[])
        self.bonusAC = bonusAC
