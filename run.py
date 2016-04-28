from Tkinter import Tk

from src.views.piano_roll import PianoRoll

if __name__ == '__main__':
    root = Tk()
    root.wm_title("Piano Roll")
    app = PianoRoll(root)
    root.mainloop()