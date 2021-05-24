import character
import item

sword = item.Weapon("boof", 1)

avery = character.Character({'avery'})

avery.equip(sword, "leftHand")
avery.unequip('leftHand')

avery.showAttributes()
avery.showSkills()
avery.showGear()
avery.showInventory()
