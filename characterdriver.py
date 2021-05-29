# pylint: disable=unused-wildcard-import

from character import *
from item import *
import resources

sword = Weapon("boof", 1)

avery = Character({'name':'avery', 'strength':8, 'boots':resources.boots, 'technology':1, 'temphp':4, 'hp':6})

avery.heal(1)
avery.hurt(2)

avery.equip(sword, 'leftHand')
avery.unequip('leftHand')

print(avery.attributes)
# avery.showAttributes()
# avery.showSkills()
# avery.showGear()
# avery.showInventory()
# avery.show()

ashrak = resources.ashrak
ashrak.show()