import character
import playerfunctions
import dmfunctions
import item
import resources

from importlib import reload

print("\nPackages imported")

factions = dmfunctions.load()

print("Factions loaded:")

print(factions.keys())

for faction, characters in factions.items():
    exec(str(faction)+'=characters')

print("Factions assigned to variables")
