def soldier(charObj):
    charObj.hitDie = 10
    charObj.bonusAttrs['constitution'] += 2
    charObj.bonusSkills['tactics'] += 1
    charObj.bonusSkills['athletics'] += 1

def scientist(charObj):
    charObj.hitDie = 8
    charObj.bonusAttrs['intelligence'] += 3
    charObj.bonusSkills['technology'] += 2
    charObj.bonusSkills['xenotechnology'] += 2

def anthropologist(charObj):
    charObj.hitDie = 8
    charObj.bonusAttrs['wisdom'] += 3
    charObj.bonusSkills['anthropology'] += 2
    charObj.bonusSkills['xenoanthropology'] += 1
    charObj.bonusSkills['diplomacy'] += 1
