import character
import item
import dmtools
import json

from os import sep


class Template(character.Character):
    def __init__(self, name=None, race=None, clas=None, slots=None):
        self.name = input("name? >>> ") if name is None else name
        self.race = input("race? >>> ") if race is None else race
        self.clas = input("clas? >>> ") if clas is None else clas

        # with open(f".{sep}races{sep}{self.race}{sep}{self.race}.json", encoding='utf-8') as f:
        #     race_defaults = json.load(f)

        if slots is None:
            self.slots = {}
            self.load_slots()
        else:
            self.slots = slots

        self = character.Character.new({'name':self.name, 'race':self.race, 'clas':self.clas, 'slots':self.slots})

    def load_slots(self):
        # getting the slots from the race allows for non-humanoids
        with open(f".{sep}races{sep}{self.race}{sep}defaults.json", encoding='utf-8') as f:
            default_slots = json.load(f)['slots']

        for slot in default_slots:
            s = input(f"{slot}? >>> ")
            self.slots[slot] = dmtools.load_item(s) if s != "" else None
            
    def save(self):
        with open(f".{sep}races{sep}{self.race}{sep}{templates}{sep}{self.name}.json", 'w+', encoding='utf-8') as f:
            json.dump(character.Character.new({'name':self.name, 'race':self.race, 'clas':self.clas, 'slots':self.slots}).get_json(), f)

    @classmethod
    def refactor(cls, file_path_no_ext):
        import traceback
        with open(file_path_no_ext + '.json') as f:
            try:
                cls(json.load(f)).save()
            except Exception:
                print(traceback.format_exc())
