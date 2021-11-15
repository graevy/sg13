import json
import os


class Clas:
    # def __init__(self, name, hit_die, bonus_attrs, bonus_skills, proficiencies=None, feats=None):
    #     self.name, self.hit_die, self.bonus_attrs, self.bonus_skills, self.proficiencies, self.feats = \
    #         name, hit_die, bonus_attrs, bonus_skills, proficiencies, feats

    @classmethod
    def create(cls, name, hit_die, bonus_attrs, bonus_skills,
    proficiencies=None, feats=None, attr_weights=None, skill_weights=None):
        with open(f'.{os.sep}classes{os.sep}{name}.json', 'w+', encoding='utf-8') as f:
            json.dump(vars(cls(name, hit_die, bonus_attrs, bonus_skills,
            proficiencies, feats, attr_weights, skill_weights)), f)


def load_clas(name):
    with open(f'.{os.sep}classes{os.sep}{name}.json', 'r', encoding='utf-8') as f:
        return json.load(f)
