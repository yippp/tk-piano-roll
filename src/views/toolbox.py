from Tkinter import *

from src.paths import *


class Toolbox(Frame):

    def __init__(self, parent, cb):
        Frame.__init__(self, parent)
        self.parent = parent
        self.cb = cb

        self._init_ui()

    def _cb(self, *args):
        self.cb(self._var.get())

    def _init_ui(self):
        self._var = IntVar()

        self._bttn_images = {
            'cursor': PhotoImage(file=SEL_IMG_PATH),
            'eraser': PhotoImage(file=ERASER_IMG_PATH),
            'pen':    PhotoImage(file=PEN_IMG_PATH)
        }

        self.cursor_bttn =  Radiobutton(self, value=0, variable=self._var,
            indicatoron=0, image=self._bttn_images['cursor'],
            offrelief=FLAT)
        self.pen_bttn = Radiobutton(self, value=1, variable=self._var,
            indicatoron=0, image=self._bttn_images['pen'],
            offrelief=FLAT)
        self.eraser_bttn = Radiobutton(self, value=2, variable=self._var,
            indicatoron=0, image=self._bttn_images['eraser'],
            offrelief=FLAT)

        self._var.trace("w", self._cb)

        self.cursor_bttn.pack(side=LEFT)
        self.pen_bttn.pack(side=LEFT)
        self.eraser_bttn.pack(side=LEFT)

    def set(self, value):
        self._var.set(value)