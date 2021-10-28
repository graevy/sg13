import tkinter as tk
import character
import item
import playertools
import rolls

class playerPanel(tk.Tk):
    def __init__(self, character, x=500, y=700):
        tk.Tk.__init__(self)
        self.geometry(f'{x}x{y}')
        self.title(character.name)
        self.playerButtons = []


player = playerPanel()
player.mainloop()
