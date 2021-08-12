import character
import item
from copy import deepcopy


# items
# TODO: this whole resource structure is a mess. I'm going to have to
# move individual items into json files and load on demand
# most of these variables don't need to be instantiated into classes either
# they can just be dicts passed to constructors as needed

helmet = item.Armor("Helmet", "Ballistic Infantry Helmet", weight=1.6, bonusAC=1)
backpack = item.Armor("Backpack", "Weatherproofed", weight=2.1)
boots = item.Armor("Boots", "Combat boots", weight=0.7)
gloves = item.Armor("Gloves", weight=0.1)
bdupants = item.Armor("BDU Pants", "Standard battle dress uniform pants", weight=1.0)
belt = item.Armor("Infantry Belt", "Pouched belt with holster", weight=0.6)
bdushirt = item.Armor("BDU Shirt", "Standard battle dress uniform shirt", weight=1.0)

p90 = item.Weapon(
    "FN P90",
    "5.7x28mm FMJ",
    weight=3.0,
    range=200,
    damage=12,
    proficiency="dexterity",
    cqcpenalty=1,
)
m24 = item.Weapon(
    "M24",
    "7.62x51mm",
    weight=7.0,
    range=800,
    damage=20,
    proficiency="dexterity",
    cqcpenalty=3,
)
zat = item.Weapon(
    "Zat'nik'tel",
    weight=1.0,
    range=75,
    damage=0,
    proficiency="dexterity",
    cqcpenalty=1,
)
matok = item.Weapon(
    "Ma'tok",
    weight=5.0,
    range=50,
    damage=30,
    proficiency="strength",
    cqcpenalty=0,
)

grenade = item.Item("Frag Grenade", "Made in the USA", weight=0.4)
c4 = item.Item("C4", "Single c4 brick", weight=0.2)

gdo = item.Item("GDO", "Iris GDO", weight=0.2)
compass = item.Item("Compass", "magnets", weight=0.1)
canteen = item.Item("Canteen", "2 liters", weight=2.1)
binoculars = item.Item("Binoculars", "Passive rangefinding, variable zoom", weight=0.7)
mre = item.Item("MRE", "Meal ready to eat", weight=0.6)
radio = item.Item("Radio", "50km unobscured maximum range", weight=0.1)
flashlight = item.Item("Flashlight", weight=0.4)
laptop = item.Item("Laptop", "Dell Latitude D600", weight=2.0)
notebook = item.Item("Notebook", weight=0.3)
camcorder = item.Item("Camcorder", weight=0.2)
iodine = item.Item("Iodine", "For water purification", weight=0.1)
harness = item.Item("Harness", "For climbing", weight=0.8)

scanner = item.Item(
    "Alteran Scanner",
    "Ranges: 50m lifesigns, 300m misc. heat, 1-100km em/radiation depending on strength. Ranges tripled but detectable in active mode.",
    weight=0.3,
)


ashrakhelmet = item.Armor("Ashrak Helmet", "Goa'uld HUD", weight=2, bonusAC=1)
ashrakchest = item.Armor("Ashrak Chestplate", "Painful to wear", weight=4, bonusAC=2)
ashraklegs = item.Armor("Ashrak Legplates", "More painful to wear", weight=3, bonusAC=1)
ashrakboots = item.Armor("Ashrak Boots", "Made for larger feet", weight=2)
ashrakmatok = item.Weapon("Ashrak Wrist-Mounted Ma'tok", "Unwieldy", weight=0, range=50, damage=30, proficiency="dexterity", proficiencytype="ranged")

jaffahelmet = item.Armor("Jaffa Cap", "Humbling", weight=1, bonusAC=1)
jaffachest = item.Armor("Jaffa Hauberk", "Surprisingly light", weight=1, bonusAC=2)
jaffabelt = item.Armor("Jaffa Belt", "Alloyed Plate", weight=1, storage=[deepcopy(zat)])
jaffalegs = item.Armor("Jaffa Chainskirt", "Sturdy", weight=2, bonusAC=1)
jaffaboots = item.Armor("Jaffa Boots", "Alloyed Plate", weight=2)


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
    head=deepcopy(helmet),
    chest=deepcopy(bdushirt),
    belt=deepcopy(belt),
    legs=deepcopy(bdupants),
    boots=deepcopy(boots)
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
    head=deepcopy(jaffahelmet),
    chest=deepcopy(jaffachest),
    belt=deepcopy(jaffabelt),
    legs=deepcopy(jaffalegs),
    boots=deepcopy(jaffaboots)
)

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
    leftHand=deepcopy(ashrakmatok),
    rightHand=deepcopy(ashrakmatok),
    head=deepcopy(ashrakhelmet),
    chest=deepcopy(ashrakchest),
    legs=deepcopy(ashraklegs),
    boots=deepcopy(ashrakboots)
)



# in case i fuck up the jsons irreversably, here's the old strings.

# characters by faction
# metuu = character.Character({}, name="Met'uu", race='jaffa', strength=14, dexterity=12, constitution=14, intelligence=16, wisdom=16, charisma=8,
# xenotechnology=3, stealth=3, anthropology=3, xenoanthropology=2, perception=3, acrobatics=1, survival=1, tactics=1, medicine=1, level=4)

# victoria = character.Character({}, name='Cadet Victoria Romanenkov', strength=12, dexterity=15, constitution=13, intelligence=14, wisdom=12, charisma=16,
# perception=1, technology=2, medicine=1, sleightofhand=1, tactics=3, stealth=2, athletics=1, diplomacy=2, level=1)

# steve = character.Character({}, name='Dr. Steven Hartman', race='human', strength=12, dexterity=14, constitution=14, intelligence=16, wisdom=14, charisma=13,
# vehicles=2, insight=1, xenotechnology=4, technology=4, perception=3, sleightofhand=2, diplomacy=1, survival=1, tactics=1, level=4)

# sabrac = character.Character({}, name='Sabrac', race='jaffa', strength=16, dexterity=10, constitution=16, intelligence=10, wisdom=14, charisma=10)


# sg13 = [metuu, victoria, steve, sabrac]

# j = character.Character({}, name='J', faction='trust/sg31', strength=10, dexterity=14, constitution=10, intelligence=16, wisdom=12, charisma=10)
# s = character.Character({}, name='S', faction='trust/sg31', strength=14, dexterity=14, constitution=12, intelligence=8, wisdom=12, charisma=8)
# o3 = character.Character({}, name='O3', faction='trust/sg31', strength=10, dexterity=12, constitution=14, intelligence=14, wisdom=16, charisma=14)
# m = character.Character({}, name='M', faction='trust/sg31', strength=16, dexterity=12, constitution=12, intelligence=8, wisdom=10, charisma=10)

# trust = [j, s, o3, m]