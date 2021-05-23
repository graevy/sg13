import resources
import item
import dmfunctions

bag = item.Armor("Backpack", "Weatherproofed", weight=2.1)
bagbag = item.Armor("Backpack", "Weatherproofed", weight=2.1, storage=[bag])

driver = resources.bdupants
driver.storage = [resources.p90, resources.gdo, bagbag]

# TODO: recursion seems to fail
driver.show()