import character
import dmfunctions
import playerfunctions
import item
import resources

print("\nPackages imported")

factions = dmfunctions.load()

print("Factions loaded:")

print(factions.keys())


for faction, characters in factions.items():
    exec(str(faction)+'=characters')

print("Factions assigned to variables")