import json
from os import sep


class Config:
    def __init__(self, name, vars):
        self.name = name
        self.vars = vars
    
    def save(self):
        with open(self.name + '.json', 'w+') as f:
            json.dump(self.vars, f)

    # TODO P1: settings must be universal
    # def handle_path_separators(self):
    #     for value in self.vars.values():
    #         if type(value) == str:
    #             value.replace("/", sep)
    

# global cfg
WEIGHT_AFFECTS_SPEED = True
BINARY_SKILLS = False

# tweaks
MAX_LEVEL = 20
MAX_ATTR = 20
MAX_SKILL = 5
BASE_SKILL_POINTS = 3
BASE_AC = 6
MELEE_RANGE = 3
DEFAULT_POINT_BUY_POINTS = 27
DEFAULT_ATTR = 8
DEFAULT_SKILL = 0
MAX_BONUS_AC_FROM_COVER = 4
COVER_INTERVAL = 100 // MAX_BONUS_AC_FROM_COVER
RANGE_EXPONENT = 2 # higher value makes ranged attacks hit less often

# dice
DICE = 3
DIE = 6

# dirs
FACTIONS_DIR = f".{sep}factions{sep}"
RACES_DIR = f".{sep}races{sep}"
CLASS_ES_DIR = f".{sep}class_es{sep}"
ITEMS_DIR = f".{sep}items{sep}"
TEMPLATES_DIR = f".{sep}npc_templates{sep}"
