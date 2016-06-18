from Tkinter import Tk

from src.views.piano_roll import PianoRoll
from src.helper import make_title

if __name__ == '__main__':
    root = Tk()
    app = PianoRoll(root)
    root.title(make_title("Untitled", False))
    root.mainloop()
