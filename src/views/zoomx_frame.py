import math
from Tkinter import *
from ..const import ZOOM_X_VALUES


class ZoomXFrame(Frame):

    def __init__(self, parent, cb):
        Frame.__init__(self, parent)
        self.parent = parent
        self.cb = cb

        self._init_ui()

    def _cb(self, *args):
        self.cb(ZOOM_X_VALUES[self.zoom_scale.get()])

    def _init_ui(self):
        self.var = IntVar()

        self.label = Label(self, text="Zoom X")
        self.zoom_scale = Scale(self, from_=0, to_=len(ZOOM_X_VALUES) - 1,
            orient=HORIZONTAL, showvalue=0, variable=self.var)
        self.zoom_scale.set(ZOOM_X_VALUES.index(1))
        self.var.trace("w", self._cb)

        self.label.pack(side=LEFT)
        self.zoom_scale.pack(side=LEFT)