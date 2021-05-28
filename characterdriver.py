# pylint: disable=unused-wildcard-import

from character import *
from item import *

sword = Weapon("boof", 1)

avery = Character({'name':'avery', })

avery.equip(sword, 'leftHand')
avery.unequip('leftHand')

print(avery.attributes)
# avery.showAttributes()
# avery.showSkills()
# avery.showGear()
# avery.showInventory()
avery.show()