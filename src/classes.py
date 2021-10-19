def soldier(charObj):
    charObj.hitDie = 10
    charObj.attributes['constitution'] += 2
    charObj.skills['tactics'] += 1
    charObj.skills['athletics'] += 1

def scientist(charObj):
    charObj.hitDie = 8
    charObj.attributes['intelligence'] += 3
    charObj.skills['technology'] += 2
    charObj.skills['xenotechnology'] += 2

def anthropologist(charObj):
    charObj.hitDie = 8
    charObj.attributes['wisdom'] += 3
    charObj.skills['anthropology'] += 2
    charObj.skills['xenoanthropology'] += 1
    charObj.skills['diplomacy'] += 1
