from os import sep

FACTIONS_DIR = f".{sep}factions{sep}"
RACES_DIR = f".{sep}races{sep}"
CLASES_DIR = f".{sep}clases{sep}"
ITEMS_DIR = f".{sep}items{sep}"
TEMPLATES_DIR = f".{sep}npc_templates{sep}"

CONFIG_DIR = f".{sep}cfg{sep}"
DICE_CONFIG_DIR = CONFIG_DIR + "diceconfig.json"

# # if i ever end up extending things
# walker = os.walk('.')

# def full_dir(root, directory):
#     return root + sep + directory + sep

# for root, directory, _ in next(walker):
#     match directory:
#         case 'factions':
#             factions_dir = full_dir(root, directory)
#         case 'races':
#             races_dir = full_dir(root, directory)
#         case 'clases':
#             clases_dir = full_dir(root, directory)
#         case 'items':
#             items_dir = full_dir(root, directory)
#         case 'templates':
#             templates_dir = full_dir(root, directory)