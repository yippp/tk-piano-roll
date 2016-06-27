from Tkinter import *

from src.helper import get_image_path


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

        self._cursor_image = PhotoImage(
            file=get_image_path('sel.gif'))
        self._pen_image = PhotoImage(
            file=get_image_path('pen.gif'))
        self._eraser_image = PhotoImage(
            file=get_image_path('eraser.gif'))

        self.cursor_bttn =  Radiobutton(
            self, value=0, variable=self._var, indicatoron=0,
            image=self._cursor_image, offrelief=FLAT)
        self.pen_bttn = Radiobutton(
            self, value=1, variable=self._var, indicatoron=0,
            image=self._pen_image, offrelief=FLAT)
        self.eraser_bttn = Radiobutton(
            self, value=2, variable=self._var, indicatoron=0,
            image=self._eraser_image, offrelief=FLAT)

        self._var.trace("w", self._cb)

        self.cursor_bttn.pack(side=LEFT)
        self.pen_bttn.pack(side=LEFT)
        self.eraser_bttn.pack(side=LEFT)

    def set(self, value):
        self._var.set(value)