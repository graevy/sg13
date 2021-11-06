class Item:
    def __init__(self, name, description=None, weight=0.0, size=2, space=0, storage=[], bonus_attrs={}, bonus_skills={}):
        self.name = name
        self.description = description
        self.weight = weight
        self.size = size # 0 is tiny, 1 is small, 2 is medium...use any signed int; it's a priority system
        self.space = space
        self.storage = storage
        self.bonus_attrs = bonus_attrs
        self.bonus_skills = bonus_skills

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

    def get_weight(self):
        """recursively gets item and storage weight
        """
        return self.weight + sum(item.get_weight() for item in self.storage)

    def get_json(self):
        """recursively serializes items
        """
        attrs = vars(self)
        attrs['storage'] = [item.get_json() for item in self.storage]
        return attrs

    def store(self, container):
        """stores self in container if container can fit self

        Args:
            container (item): to store in
        """
        if self.size < container.size and len(container.storage) < container.space:
            container.storage.append(self)
        else:
            print("can't fit!")
            return False

    # # this only gets used on refactoring, and should be excluded from potential releases
    # def save(self):
    #     with open(f'./items/{self.name}.json', 'w+', encoding='utf-8') as f:
    #         json.dump(self.get_json(), f)

    # @classmethod
    # def load(cls, name):
    #     with open(f'./items/{name}.json') as f:
    #         return cls(**json.load(f))



class Weapon(Item):
    def __init__(self, name, description=None, weight=0.0, size=2, space=0, \
                    storage=[], bonus_attrs={}, bonus_skills={}, \
                    range=3, damage=8, proficiency='strength', proficiency_type='melee', cqc_penalty=0):

        super().__init__(name, description, weight, size, space, storage, bonus_attrs, bonus_skills)

        self.range, self.damage, self.proficiency, self.proficiency_type, self.cqc_penalty = \
        range, damage, proficiency, proficiency_type, cqc_penalty


class Armor(Item):
    def __init__(self, name, description=None, weight=0.0, size=2, space=0, \
                    storage=[], bonus_attrs={}, bonus_skills={}, \
                    bonus_ac=0):

        super().__init__(name, description, weight, size, space, storage, bonus_attrs, bonus_skills)

        self.bonus_ac = bonus_ac
