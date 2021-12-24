# TODO P3:
# documentation for the defaults
# refactoring away from "proficiency" and "proficiency_type". terrible names, terrible mechanics, what were you thinking

MELEE_RANGE = 3

ITEM_DEFAULTS = {'name':'item', 'description':None, 'weight':0.0, 'size':2, 'space':0, 'storage':[], 'bonus_attrs':{}, 'bonus_skills':{}}
WEAPON_DEFAULTS = {'range_':MELEE_RANGE, 'damage':0, 'proficiency':'strength', 'proficiency_type':'melee', 'cqc_penalty':0}
ARMOR_DEFAULTS = {'bonus_ac':0}


# the unsafe character.Character constructor ultimately simplified so much code around extensibility that i decided to standardize it into the item class
# item.Weapon.__init__ ended up taking 13 variables and called super().__init__ with 8 variables. there is an attrs module to handle exactly this
# but one of the goals of this project for me was no external dependencies
class Item:
    def __init__(self, attrs: dict):
        self.__dict__ |= attrs

    @classmethod
    def create(cls, attrs: dict):
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
    def create(cls, attrs: dict):
        return cls(ITEM_DEFAULTS | WEAPON_DEFAULTS | attrs)


class Armor(Item):
    @classmethod
    def create(cls, attrs: dict):
        return cls(ITEM_DEFAULTS | ARMOR_DEFAULTS | attrs)