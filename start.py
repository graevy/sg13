from dmtools import load

print("\nPackages imported")

factions = load()

print("Factions loaded:")

print(factions.keys())

for faction, characters in factions.items():
    exec(str(faction)+'=characters')

print("Factions assigned to variables")
