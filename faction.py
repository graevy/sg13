# this is probably what I should've done from the start
# immediately apparent to me after I rewrote the load function
# i'll see about incorporating it later

class Faction:
    def __init__(self, name, parent=None, children=[], characters=[]):
        self.name, self.parent, self.children, self.characters = \
            name, parent, children, characters
        self.childrenNames = [x.name for x in self.children]

    def populate(self, characters):
        self.characters += characters

    def makeChild(self, name, children=[], characters=[]):
        child = Faction(name, parent=self, children=children, characters=characters)
        self.children.add(child)
        self.childrenNames.append(child.name)
        return child

    def hasChildNamed(self, name):
        if name in self.childrenNames:
            return True
        else:
            return False

    def show(self, spacing=''):
        """recursively prints faction and children
        """
        if self.children:
            print(spacing + f"{self.name} contains: {self.childrenNames}")
        spacing += '    '
        for child in self.children:
            child.show(spacing)
