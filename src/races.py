def human(char_obj): # +1 to all
    char_obj.bonus_attrs = {attr_name:attr_value+1 for attr_name,attr_value in char_obj.bonus_attrs.items()}

def jaffa(char_obj):
    char_obj.bonus_attrs['constitution'] += 2
    char_obj.bonus_attrs['wisdom'] += 2

def goauld(char_obj):
    char_obj.bonus_attrs['constitution'] += 2
    char_obj.bonus_attrs['intelligence'] += 2
    char_obj.bonus_attrs['charisma'] += 2
    char_obj.bonus_attrs['wisdom'] -= 2

def tokra(char_obj):
    # :^)
    goauld(char_obj)
