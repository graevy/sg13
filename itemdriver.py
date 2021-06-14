import resources
import item
import dmfunctions
from copy import deepcopy

bag = deepcopy(resources.backpack)
bagbag = item.Armor("Backpack", "Weatherproofed", weight=2.1, storage=[bag])

driver = resources.bdupants
driver.storage = [resources.p90, resources.gdo, bagbag]

driver.show()
print(driver.getWeight())

# a = item.Armor('test', 'a test thing', bonusAC=1)
# print(a.name)
# b = item.Weapon('foo', 'bar')
# print(b.range)