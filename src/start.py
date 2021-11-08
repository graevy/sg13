try:
    from importlib import reload
    import traceback

    import character
    import playertools
    from dmtools import *
    import item
    import race
    import clas

    import rolls

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

# (for releases)

# def main():
#     try:
#         from dmtools import load

#         print("Packages imported")

#         try:
#             factions = load()
#             print(f"Factions loaded:\n{factions}")
#         except Exception:
#             # blair: traceback gives the full stack, including exception name
#             print(f"Factions failed to load:")
#             print(traceback.format_exc())

#     except ImportError as e:
#         print(f"Packages failed to import:")
#         print(traceback.format_exc())


# if __name__ == "__main__":
#     main()