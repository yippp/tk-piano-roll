from Tkinter import Tk

from src.views.piano_roll import PianoRoll
from src.views.piano_roll_menu import PianoRollMenu

if __name__ == '__main__':
    root = Tk()
    root.wm_title("Piano Roll")
    menu = PianoRollMenu()
    root.config(menu=menu)
    app = PianoRoll(root)
    root.mainloop()
