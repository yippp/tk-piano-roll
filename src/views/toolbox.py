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
            'cursor': PhotoImage(file=CURSOR_TOOL_IMG_PATH),
            'eraser': PhotoImage(file=ERASER_TOOL_IMG_PATH),
            'pen':    PhotoImage(file=PEN_TOOL_IMG_PATH)
        }

        self._cursor_bttn =  Radiobutton(self, value=0, variable=self._var,
            image=self._bttn_images['cursor'], indicatoron=0, padx=2, pady=2)
        self._pen_bttn = Radiobutton(self, value=1, variable=self._var,
            image=self._bttn_images['pen'], indicatoron=0, padx=10, pady=10)
        self._eraser_bttn = Radiobutton(self, value=2, variable=self._var,
            image=self._bttn_images['eraser'], indicatoron=0, padx=2, pady=2)

        self._var.trace("w", self._cb)

        self._cursor_bttn.pack(side=LEFT)
        self._pen_bttn.pack(side=LEFT)
        self._eraser_bttn.pack(side=LEFT)
