import tkinter as tk
import rolls
import dmtools
import inspect

class DMPanel(tk.Tk):
    def __init__(self, width=700, height=350):
        super().__init__()
        self.title("SG13 DM Toolkit")
        # self.label = tk.Label(self, text="SG13 DM Toolkit")
        self.geometry(f"{width}x{350}")


        # for readability
        dmFns = [fnTuple for fnTuple in inspect.getmembers(dmtools, inspect.isfunction)]
        self.buttons = [tk.Button(text=fnName, command=fn) for fnName,fn in dmFns]
        
        rollFns = [fnTuple for fnTuple in inspect.getmembers(rolls, inspect.isfunction)]
        self.buttons += [tk.Button(text=fnName, command=fn) for fnName,fn in rollFns]

        # populating the GUI
        frame = tk.Frame()
        

if __name__ == '__main__':
    panel = DMPanel()
    panel.mainloop()