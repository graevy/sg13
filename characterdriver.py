from character import *
from item import *

sword = Weapon('boof', 1, None)


avery = Character('avery')

nerd = Character('nerd')

avery.equip(sword, 'leftHand')

avery.show()
