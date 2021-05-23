import character
import item


# factions
# factions = dmfunctions.loadcharacters()

# characters by faction
# naamah = character.Character("Met'uu", race='jaffa', strength=14, dexterity=12, constitution=14, intelligence=16, wisdom=16, charisma=8,
# xenotechnology=3, stealth=3, anthropology=3, xenoanthropology=2, perception=3, acrobatics=1, survival=1, tactics=1, medicine=1, level=4)

# victoria = character.Character('Cadet Victoria Romanenkov', strength=12, dexterity=15, constitution=13, intelligence=14, wisdom=12, charisma=16,
# perception=1, technology=2, medicine=1, sleightofhand=1, tactics=3, stealth=2, athletics=1, diplomacy=2, level=1)

# steve = character.Character('Dr. Steven Hartman', race='human', strength=12, dexterity=14, constitution=14, intelligence=16, wisdom=14, charisma=13,
# vehicles=2, insight=1, xenotechnology=4, technology=4, perception=3, sleightofhand=2, diplomacy=1, survival=1, tactics=1, level=4)

# sabrac = character.Character('Sabrac', race='jaffa', strength=16, dexterity=10, constitution=16, intelligence=10, wisdom=14, charisma=10)

# sg13 = [naamah, victoria, steve, sabrac]

# j = character.Character('J', faction='sg31', strength=10, dexterity=14, constitution=10, intelligence=16, wisdom=12, charisma=10)
# s = character.Character('S', faction='sg31', strength=14, dexterity=14, constitution=12, intelligence=8, wisdom=12, charisma=8)
# o3 = character.Character('O3', faction='sg31', strength=10, dexterity=12, constitution=14, intelligence=14, wisdom=16, charisma=14)
# m = character.Character('M', faction='sg31', strength=16, dexterity=12, constitution=12, intelligence=8, wisdom=10, charisma=10)

# sg31 = [j, s, o3, m]

# generic NPCs
# TODO: equip NPCs

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

# items
# TODO: create premade item packs for sgc personnel

backpack = item.Armor("Backpack", "Weatherproofed", weight=2.1)
boots = item.Armor("Boots", "Combat boots", weight=0.7)
gloves = item.Armor("Gloves", weight=0.1)
bdupants = item.Armor(
    "BDU Pants", "Standard battle dress uniform pants", weight=1.0
)
bdushirt = item.Armor(
    "BDU Shirt", "Standard battle dress uniform shirt", weight=1.0
)

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
