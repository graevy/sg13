class Stat:
    def update(self):
        self.value = self.base + self.bonus
        self.mod = self.value - 10 >> 1

    def __init__(self, name, base, bonus=0):
        self.name, self.base, self.bonus = name, base, bonus
        self.update()

    def set_base(self, new):
        self.base = new
        self.update()

    def serialize(self):
        return (self.name, self.base, self.bonus)
        