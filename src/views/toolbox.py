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
            'cursor': PhotoImage(file=TOOL_CURSOR_IMG_PATH),
            'eraser': PhotoImage(file=TOOL_ERASER_IMG_PATH),
            'pen':    PhotoImage(file=TOOL_PEN_IMG_PATH)
        }

        self.cursor_bttn =  Radiobutton(self, value=0, variable=self._var,
            image=self._bttn_images['cursor'], indicatoron=0, padx=2, pady=2)
        self.pen_bttn = Radiobutton(self, value=1, variable=self._var,
            image=self._bttn_images['pen'], indicatoron=0, padx=10, pady=10)
        self.eraser_bttn = Radiobutton(self, value=2, variable=self._var,
            image=self._bttn_images['eraser'], indicatoron=0, padx=2, pady=2)

        self._var.trace("w", self._cb)

        self.cursor_bttn.pack(side=LEFT)
        self.pen_bttn.pack(side=LEFT)
        self.eraser_bttn.pack(side=LEFT)

    def set(self, value):
        self._var.set(value)