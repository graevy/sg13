import json
import os

import cfg.dirs

class Clas:
    # def __init__(self, name, hit_die, bonus_attrs, bonus_skills, proficiencies=None, feats=None):
    #     self.name, self.hit_die, self.bonus_attrs, self.bonus_skills, self.proficiencies, self.feats = \
    #         name, hit_die, bonus_attrs, bonus_skills, proficiencies, feats

    def create(name, hit_die, bonus_attrs, bonus_skills,
        proficiencies=None, feats=None, attr_weights=None, skill_weights=None):

        attrs = {'name':name, 'hit_die':hit_die, 'bonus_attrs':bonus_attrs, 'bonus_skills':bonus_skills,
            'proficiencies':proficiencies, 'feats':feats, 'attr_weights':attr_weights, 'skill_weights':skill_weights}

        with open(cfg.dirs.CLASES_DIR + name + '.json', 'w+', encoding='utf-8') as f:
            json.dump(attrs, f)


def load_clas(name):
    with open(cfg.dirs.CLASES_DIR + name + '.json', 'r', encoding='utf-8') as f:
        return json.load(f)
