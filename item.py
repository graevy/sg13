class Item:
    def __init__(self, name, description=None, weight=0, storage=[]):
        self.name = name
        self.description = description
        self.weight = weight
        self.storage = storage

    def __str__(self):
        return self.name

    def getstorage(self):
        return self.storage


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

    def get_proficiency(self):
        return self.proficiency

    def get_proficiencytype(self):
        return self.proficiencytype

    def reload(self):
        # TODO
        pass


class Armor(Item):
    def __init__(
        self, name, description=None, weight=0.0, bonusAC=0, storage=[]
    ):
        Item.__init__(self, name, description=None, weight=0.0, storage=[])
        self.bonusAC = bonusAC
