try:
    import character
    import playertools
    from dmtools import *
    import item
    import resources

    from importlib import reload
    print("Packages imported")

except Exception as e:
    print(f"Packages failed to import: {e}")

try:
    factions = load()
    print(f"Factions loaded:\n{factions}")
except Exception as e:
    print(f"Factions failed to load: {e}")
