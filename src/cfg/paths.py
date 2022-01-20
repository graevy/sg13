from os import sep

FACTIONS_PATH = f".{sep}factions{sep}"
RACES_PATH = f".{sep}races{sep}"
CLASSES_PATH = f".{sep}class_es{sep}"
ITEMS_PATH = f".{sep}items{sep}"
TEMPLATES_PATH = f".{sep}npc_templates{sep}"

CONFIG_PATH = f".{sep}cfg{sep}"
DICE_CONFIG_PATH = CONFIG_PATH + "diceconfig.json"

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
#         case 'class_es':
#             class_es_dir = full_dir(root, directory)
#         case 'items':
#             items_dir = full_dir(root, directory)
#         case 'templates':
#             templates_dir = full_dir(root, directory)