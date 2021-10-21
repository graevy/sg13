class Item:
    def __init__(self, name, description=None, weight=0.0, size=2, slots=0, storage=[], bonusAttrs={}, bonusSkills={}):
        self.name = name
        self.description = description
        self.weight = weight
        self.size = size # 0 is tiny, 1 is small, 2 is medium...use any signed int; it's a priority system
        self.slots = slots
        self.storage = storage
        self.bonusAttrs = bonusAttrs
        self.bonusSkills = bonusSkills

    def __str__(self):
        return self.name+': '+self.description

    def show(self, spacing=''):
        """recursively pretty-prints item & storage contents
        """
        if self.storage:
            print(spacing + f"{self.name} contains: {[item.name for item in self.storage]}")
        spacing += '    '
        for item in self.storage:
            item.show(spacing)

    def getWeight(self):
        """recursively gets item and storage weight
        """
        return self.weight + sum([item.getWeight() for item in self.storage])

    def getJSON(self):
        """recursively serializes items
        """
        attrs = vars(self)
        attrs['storage'] = [item.getJSON() for item in self.storage]
        return attrs

    def store(self, container):
        """stores self in container if container can fit self

        Args:
            container (item): to store in
        """
        if self.size < container.size and len(container.storage) < container.slots:
            container.storage.append(self)
        else:
            print("can't fit!")
            return False


class Weapon(Item):
    def __init__(self, name, description=None, weight=0.0, size=2, slots=0, \
                    storage=[], bonusAttrs={}, bonusSkills={}, \
                    range=3, damage=8, proficiency='strength', proficiencytype='melee', cqcpenalty=0):

        super().__init__(name, description, weight, size, slots, storage, bonusAttrs, bonusSkills)

        self.range, self.damage, self.proficiency, self.proficiencytype, self.cqcpenalty = \
        range, damage, proficiency, proficiencytype, cqcpenalty


class Armor(Item):
    def __init__(self, name, description=None, weight=0.0, size=2, slots=0, \
                    storage=[], bonusAttrs={}, bonusSkills={}, \
                    bonusAC=0):

        super().__init__(name, description, weight, size, slots, storage, bonusAttrs, bonusSkills)

        self.bonusAC = bonusAC
