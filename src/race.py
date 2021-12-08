import json
import os


class Race:
    def create(name, bonus_attrs, bonus_skills, proficiencies=None, feats=None):
        attrs = {'name':name, 'bonus_attrs':bonus_attrs, 'bonus_skills':bonus_skills, 'proficiencies':proficiencies, 'feats':feats}
        with open(f'.{os.sep}races{os.sep}{name}.json', 'w+', encoding='utf-8') as f:
            json.dump(attrs, f)

def load_race(name):
    with open(f'.{os.sep}races{os.sep}{name}.json', 'r', encoding='utf-8') as f:
        return json.load(f)
