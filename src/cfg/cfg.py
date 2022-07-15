import json
import sys
from os import sep as SEP

# who watches the watchers?
CFG_DIR = f".{SEP}cfg{SEP}cfg.json"


# i decided to do this for extensibility,
# and the convenience of the dot operator.
# probably yagni, just use a dictionary?
class Vars:
    """containerized dict of config variables
    """
    def __init__(self, configs):
        self.__dict__ |= configs

class Config:
    """associated methods of Vars struct
    """
    def __init__(self, configs, name=None):
        self.configs = Vars(configs)
        self.name = name
    
    def save(self):
        for k,v in self.data.items():
            if type(v) == str:
                self.data[k] = v.replace(SEP, '/')

        with open(self.name + '.json', 'w+') as f:
            json.dump(self.data, f)

    @classmethod
    def load(cls, config_json):
        with open(config_json) as f:
            cls = json.load(f)

        for k,v in cls.items():
            if type(v) == str:
                cls[k] = v.replace('/', SEP)

        return cls

    def set(self, property, value):
        self.configs.__dict__[property] = value

cfg = Config(Config.load(config_json=CFG_DIR))

# can't believe i thought this was a good idea when i was writing it
# leaving this as a reminder to not just do things because you can
# globals().update(Config.load(config_json=CFG_DIR))