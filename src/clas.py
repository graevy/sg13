import json


class Clas:
    # def __init__(self, name, hit_die, bonus_attrs, bonus_skills, proficiencies=None, feats=None):
    #     self.name, self.hit_die, self.bonus_attrs, self.bonus_skills, self.proficiencies, self.feats = \
    #         name, hit_die, bonus_attrs, bonus_skills, proficiencies, feats

    @classmethod
    def create(cls, name, hit_die, bonus_attrs, bonus_skills, proficiencies=None, feats=None):
        with open(f'./classes/{name}.json', 'w+', encoding='utf-8') as f:
            json.dump(vars(cls(name, hit_die, bonus_attrs, bonus_skills, proficiencies, feats)), f)

def load_clas(name):
    with open(f'./classes/{name}.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# clas.Clas.create("anthropologist", 8, {'strength':0, 'dexterity':0, 'constitution':0, 'intelligence':0, 'wisdom':3, 'charisma':0}, {name:0 for name in character.defaults['skills']} | {'anthropology':2, 'xenoanthropology':1, 'diplomacy':1})