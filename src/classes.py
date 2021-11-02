def soldier(char_obj):
    char_obj.hit_die = 10
    char_obj.bonus_attrs['constitution'] += 2
    char_obj.bonus_skills['tactics'] += 1
    char_obj.bonus_skills['athletics'] += 1

def scientist(char_obj):
    char_obj.hit_die = 8
    char_obj.bonus_attrs['intelligence'] += 3
    char_obj.bonus_skills['technology'] += 2
    char_obj.bonus_skills['xenotechnology'] += 2

def anthropologist(char_obj):
    char_obj.hit_die = 8
    char_obj.bonus_attrs['wisdom'] += 3
    char_obj.bonus_skills['anthropology'] += 2
    char_obj.bonus_skills['xenoanthropology'] += 1
    char_obj.bonus_skills['diplomacy'] += 1
