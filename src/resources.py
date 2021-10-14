import character
import item
from copy import deepcopy


# items
# TODO: this whole resource structure is a mess. I'm going to have to
# move individual items into json files and load on demand
# most of these variables don't need to be instantiated into classes either
# they can just be dicts passed to constructors as needed

helmet = item.Armor("Helmet", "Ballistic Infantry Helmet", weight=1.6, size=2, bonusAC=1)
backpack = item.Armor("Backpack", "Weatherproofed", weight=2.1, size=3, slots=6)
boots = item.Armor("Boots", "Combat boots", weight=0.7, size=2)
gloves = item.Armor("Gloves", weight=0.1, size=1)
bdupants = item.Armor("BDU Pants", "Standard battle dress uniform pants", weight=1.0, slots=2, size=2)
belt = item.Armor("Infantry Belt", "Pouched belt with holster", weight=0.6, slots=4, size=2)
bdushirt = item.Armor("BDU Shirt", "Standard battle dress uniform shirt", weight=1.0, slots=2, size=2)

p90 = item.Weapon(
    "FN P90",
    "5.7x28mm FMJ",
    weight=3.0,
    range=200,
    damage=12,
    proficiency="dexterity",
    cqcpenalty=1,
    size=2
)
m24 = item.Weapon(
    "M24",
    "7.62x51mm",
    weight=7.0,
    range=800,
    damage=20,
    proficiency="dexterity",
    cqcpenalty=3,
    size=2
)
zat = item.Weapon(
    "Zat'nik'tel",
    weight=1.0,
    range=75,
    damage=0,
    proficiency="dexterity",
    cqcpenalty=1,
    size=1,
)
matok = item.Weapon(
    "Ma'tok",
    weight=5.0,
    range=50,
    damage=30,
    proficiency="strength",
    cqcpenalty=0,
    size=3,
)

grenade = item.Item("Frag Grenade", "Made in the USA", weight=0.4, size=1)
c4 = item.Item("C4", "Single c4 brick", weight=0.2, size=1)

gdo = item.Item("GDO", "Iris GDO", weight=0.2, size=1)
compass = item.Item("Compass", "magnets", weight=0.1, size=1)
canteen = item.Item("Canteen", "2 liters", weight=2.1, size=2)
binoculars = item.Item("Binoculars", "Passive rangefinding, variable zoom", weight=0.7, size=2)
mre = item.Item("MRE", "Meal ready to eat", weight=0.6, size=1)
radio = item.Item("Radio", "50km unobscured maximum range", weight=0.1, size=1)
flashlight = item.Item("Flashlight", weight=0.4, size=1)
laptop = item.Item("Laptop", "Dell Latitude D600", weight=2.0, size=2)
notebook = item.Item("Notebook", weight=0.3, size=2)
camcorder = item.Item("Camcorder", weight=0.2, size=1)
iodine = item.Item("Iodine", "For water purification", weight=0.1, size=1)
harness = item.Item("Harness", "For climbing", weight=0.8, size=2)

scanner = item.Item(
    "Alteran Scanner",
    "Ranges: 50m lifesigns, 300m misc. heat, 1-100km em/radiation depending on strength. Ranges tripled but detectable in active mode.",
    weight=0.3,
    size=2
)


ashrakhelmet = item.Armor("Ashrak Helmet", "Goa'uld HUD", weight=2, bonusAC=1, size=2)
ashrakchest = item.Armor("Ashrak Chestplate", "Painful to wear", weight=4, bonusAC=2, size=3)
ashraklegs = item.Armor("Ashrak Legplates", "More painful to wear", weight=3, bonusAC=1, size=3)
ashrakboots = item.Armor("Ashrak Boots", "Made for larger feet", weight=2, size=2)
ashrakmatok = item.Weapon("Ashrak Wrist-Mounted Ma'tok", "Unwieldy", weight=0, size=2, range=50, damage=30, proficiency="dexterity", proficiencytype="ranged")

jaffahelmet = item.Armor("Jaffa Cap", "Humbling", weight=1, bonusAC=1, size=2)
jaffachest = item.Armor("Jaffa Hauberk", "Surprisingly light", weight=1, bonusAC=2, size=3)
jaffabelt = item.Armor("Jaffa Belt", "Alloyed Plate", weight=1, size=2, storage=[deepcopy(zat)], slots=4)
jaffalegs = item.Armor("Jaffa Chainskirt", "Sturdy", weight=2, bonusAC=1, size=3)
jaffaboots = item.Armor("Jaffa Boots", "Alloyed Plate", weight=2, size=2)


airman = character.Character(
    {},
    name="airman",
    hitdie=10,
    hp=10,
    dexterity=12,
    constitution=12,
    anthropology=1,
    technology=1,
    sleightofhand=1,
    stealth=1,
    perception=2,
    tactics=3,
    athletics=3,
    acrobatics=3,
    slots={
    'head':deepcopy(helmet),
    'chest':deepcopy(bdushirt),
    'belt':deepcopy(belt),
    'legs':deepcopy(bdupants),
    'boots':deepcopy(boots)
    }
)

jaffa = character.Character(
    {},
    name="jaffa",
    race="jaffa",
    clas="guardian",
    hitdie=10,
    hp=10,
    strength=12,
    dexterity=12,
    constitution=12,
    charisma=8,
    xenoanthropology=1,
    xenotechnology=1,
    stealth=1,
    perception=1,
    survival=2,
    tactics=1,
    athletics=2,
    acrobatics=1,
    slots={
    'leftHand':deepcopy(matok),
    'head':deepcopy(jaffahelmet),
    'chest':deepcopy(jaffachest),
    'belt':deepcopy(jaffabelt),
    'legs':deepcopy(jaffalegs),
    'boots':deepcopy(jaffaboots)
    }
)
jaffa.slots['belt'].storage.append(deepcopy(zat))

asgard = character.Character(
    {},
    name="asgard",
    race="asgard",
    hitdie=6,
    hp=6,
    speed=20,
    strength=4,
    dexterity=8,
    constitution=6,
    intelligence=16,
    wisdom=14,
    charisma=8,
    anthropology=3,
    xenoanthropology=4,
    diplomacy=2,
    medicine=3,
    vehicles=1,
    technology=3,
    xenotechnology=4,
    insight=1,
)

goauld = character.Character(
    {},
    name="goauld",
    race="goauld",
    clas="system lord",
    hitdie=12,
    hp=12,
    strength=14,
    dexterity=14,
    constitution=16,
    intelligence=14,
    wisdom=10,
    charisma=14,
    acting=1,
    anthropology=1,
    xenoanthropology=4,
    medicine=4,
    vehicles=2,
    technology=2,
    xenotechnology=3,
    sleightofhand=1,
    stealth=1,
    insight=1,
    perception=2,
    survival=1,
    tactics=1,
    athletics=2,
    acrobatics=2,
)

ashrak = character.Character(
    {},
    name='ashrak', 
    race='ashrak', 
    clas='soldier', 
    hitdie=20, 
    hp=20, 
    strength=16, 
    dexterity=12, 
    constitution=20, 
    intelligence=6, 
    wisdom=12, 
    charisma=4,
    tactics=1,
    athletics=5,
    acrobatics=2,
    slots= {
    'leftHand':deepcopy(ashrakmatok),
    'rightHand':deepcopy(ashrakmatok),
    'head':deepcopy(ashrakhelmet),
    'chest':deepcopy(ashrakchest),
    'legs':deepcopy(ashraklegs),
    'boots':deepcopy(ashrakboots)
    }
)

# import json

# for k,v in list(globals().items()):
#     if type(v) == item.Item or type(v) == item.Weapon or type(v) == item.Armor or type(v) == character.Character:
#         with open('./src/items/'+k, 'w+') as f:
#             json.dump(v.getJSON(), f)
