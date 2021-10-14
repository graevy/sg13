try:
    from importlib import reload
    import traceback

    import character
    import playertools
    from dmtools import *
    import item
    import resources

    print("Packages imported")

except Exception:
    print(f"Packages failed to import:")
    print(traceback.format_exc())

try:
    factions = load()
    print(f"Factions loaded:\n{factions}")
except Exception:
    print(f"Factions failed to load:")
    print(traceback.format_exc())
