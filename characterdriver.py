from character import *
from item import *

sword = Weapon("boof", 1, None)

avery = Character({'avery'})

avery.equip(sword, "leftHand")

avery.show()

avery.unequip(sword, "leftHand")

avery.show()