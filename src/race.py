import json


# i'm still not sure what implementation is best for races and classes but i think saving/loading
# is better than just the functions i used to have. TODO P2: this class is a placeholder, ditto for clas.py
# i'm debating internally how best to implement a race that has, for instance, a slow movement speed
class Race:
    # def __init__(self, name, bonus_attrs, bonus_skills, proficiencies=None, feats=None):
    #     self.name, self.bonus_attrs, self.bonus_skills, self.proficiencies, self.feats = \
    #         name, bonus_attrs, bonus_skills, proficiencies, feats
    
    @classmethod
    def create(cls, name, bonus_attrs, bonus_skills, proficiencies=None, feats=None):
        with open(f'./races/{name}.json', 'w+', encoding='utf-8') as f:
            json.dump(vars(cls(name, bonus_attrs, bonus_skills, proficiencies, feats)), f)

def load_race(name):
    with open(f'./races/{name}.json', 'r', encoding='utf-8') as f:
        return json.load(f)
