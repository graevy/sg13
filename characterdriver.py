from character import *
from item import *

sword = Weapon("boof", 1)

avery = Character({'avery'})

avery.equip(sword, "leftHand")
avery.unequip('leftHand')

avery.showAttributes()
avery.showSkills()
avery.showGear()
avery.showInventory()
