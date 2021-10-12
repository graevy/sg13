class Item:
    def __init__(self, name, description=None, weight=0.0, storage=[]):
        self.name = name
        self.description = description
        self.weight = weight
        self.storage = storage

    def __str__(self):
        return self.name+': '+self.description

    def show(self, spacing=''):
        """recursively pretty-prints item storage contents
        """
        if self.storage:
            print(spacing + f"{self.name} contains: {[item.name for item in self.storage]}")
        spacing += '    '
        for item in self.storage:
            item.show(spacing)

    def getWeight(self):
        """recursively gets item and storage weight
        """
        weight = self.weight
        for item in self.storage:
            weight += item.getWeight()
        return weight

    def getJSON(self):
        """recursively serializes items
        """
        attrs = vars(self)
        attrs['storage'] = [item.getJSON() for item in self.storage]
        return attrs


class Weapon(Item):
    def __init__(self, name, description=None, weight=0.0, storage=[], \
    range=3, damage=8, proficiency='strength', proficiencytype='melee', cqcpenalty=0):

        super().__init__(name, description, weight, storage)

        self.range, self.damage, self.proficiency, self.proficiencytype, self.cqcpenalty = \
        range, damage, proficiency, proficiencytype, cqcpenalty


class Armor(Item):
    def __init__(self, name, description=None, weight=0.0, storage=[], bonusAC=0):

        super().__init__(name, description, weight, storage)
        self.bonusAC = bonusAC
