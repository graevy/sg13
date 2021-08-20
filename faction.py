# this is probably what I should've done from the start
# immediately apparent to me after I rewrote the load function
# i'll see about incorporating it later

class Faction:
    def __init__(self, name, parent=None, children=[], characters=[]):
        self.name, self.parent, self.children, self.characters = \
            name, parent, children, characters
