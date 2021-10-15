def main():
    try:
        from dmtools import load

        print("Packages imported")

        try:
            factions = load()
            print(f"Factions loaded:\n{factions}")
        except Exception:
            # What exceptions can be passed up to here? Make it more specific. 
            print(f"Factions failed to load:")
            print(traceback.format_exc())

    except ImportError as e:
        print(f"Packages failed to import:")
        print(traceback.format_exc())


if __name__ == "__main__":
    main()