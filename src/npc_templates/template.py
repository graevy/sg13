import character
import item
import dmtools
import json
import os


class Template:
    def __init__(self, name, race, clas, faction, slots=None):
        if slots is None or slots == {}:
            self.slots = self.load_slots()
        else:
            self.slots = slots
        self.name = name
        self.race = race
        self.clas = clas
        self.faction = faction

    def load_slots(self):
        # race extensibility
        with open(f".{os.sep}races{os.sep}{self.race}.json", encoding='utf-8') as f:
            default_slots = json.load(f)['slots']

        for slot in default_slots:
            self.slots[slot] = dmtools.load_item(input(f"{slot}? >>> ")) if input != "" else None
            
    def save(self, template_dir=f".{os.sep}npc_templates{os.sep}"):
        with open(template_dir + self.name + '.json', 'w+', encoding='utf-8') as f:
            json.dump(character.Character.new(name=self.name, race=self.race, clas=self.clas, slots=self.slots, faction=self.faction).get_json(), f)

# airman = npc_templates.template.Template(name='airman',race='human',clas='soldier',faction='sgc')
# airman.load_slots()