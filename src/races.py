def human(charObj): # +1 to all
    charObj.attributes = {attrName:attrValue+1 for attrName,attrValue in charObj.attributes.items()}

def jaffa(charObj):
    charObj.attributes['constitution'] += 2
    charObj.attributes['wisdom'] += 2

def goauld(charObj):
    charObj.attributes['constitution'] += 2
    charObj.attributes['intelligence'] += 2
    charObj.attributes['charisma'] += 2
    charObj.attributes['wisdom'] -= 2

def tokra(charObj):
    # :^)
    goauld(charObj)
