def human(charObj): # +1 to all
    charObj.bonusAttrs = {attrName:attrValue+1 for attrName,attrValue in charObj.bonusAttrs.items()}

def jaffa(charObj):
    charObj.bonusAttrs['constitution'] += 2
    charObj.bonusAttrs['wisdom'] += 2

def goauld(charObj):
    charObj.bonusAttrs['constitution'] += 2
    charObj.bonusAttrs['intelligence'] += 2
    charObj.bonusAttrs['charisma'] += 2
    charObj.bonusAttrs['wisdom'] -= 2

def tokra(charObj):
    # :^)
    goauld(charObj)
