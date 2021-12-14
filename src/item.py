ITEM_DEFAULTS = {'name':'item', 'description':None, 'weight':0.0, 'size':2, 'space':0, 'storage':[], 'bonus_attrs':{}, 'bonus_skills':{}}
WEAPON_DEFAULTS = {'max_range':3, 'damage':8, 'proficiency':'strength', 'proficiency_type':'melee', 'cqc_penalty':0}
ARMOR_DEFAULTS = {'bonus_ac':0}

class Item:
    def __init__(self, attrs):
        self.__dict__ |= attrs

    @classmethod
    def create(cls, attrs):
        return cls(ITEM_DEFAULTS | attrs)

    def __str__(self):
        return self.name + ': ' + self.description

    def show(self, spacing=''):
        """recursively pretty-prints item & storage contents
        """
        if self.storage:
            print(spacing + self.name + ' contains: ' + ', '.join(item.name for item in self.storage))

        for item in self.storage:
            item.show(spacing + '    ')

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


class Weapon(Item):
    @classmethod
    def create(cls, attrs):
        return cls(ITEM_DEFAULTS | WEAPON_DEFAULTS | attrs)


class Armor(Item):
    @classmethod
    def create(cls, attrs):
        return cls(ITEM_DEFAULTS | ARMOR_DEFAULTS | attrs)