# because bonuses can also come from items, feats, etc,
# a centralized stat class doesn't make as much sense as previously thought
# the ideal solution is to keep track of where all bonuses come from

# individual stat instances need to communicate with bonus sources about which bonus to extract
# sources need to have stat dictionaries of {UUID: value}


from dataclasses import dataclass


@dataclass
class Stat:
    name: str
    bonus_sources: list
    base: int = 0
    bonus: int = 0
    value: int = 0

    def get_bonus(self):
        return sum(source.bonus for source in self.bonus_sources)

    def get_value(self):
        return self.base + self.get_bonus

    def serialize(self):
        """it's just self.__dict__"""
        return self.__dict__

    @classmethod
    def deserialize(cls, d):
        return cls(*d.values())

class Attribute(Stat):
    def get_mod(self):
        return self.value - 10 >> 1

class Skill(Stat):
    def get_mod(self):
        return self.value