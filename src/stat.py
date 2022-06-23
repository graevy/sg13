class Stat:
    def __init__(self, name, value):
        self.name, self.value = name, value
    def get_value(self):
        return self.value
    def set_value(self, value):
        self.value = value


class Skill(Stat):
    def __init__(self, name, value):
        super().__init__(name, value)

class Attribute(Stat):
    def __init__(self, name, value):
        super().__init__(name, value)