from Tkinter import *
from ttk import Combobox
from ..const import SNAP_DICT


class SnapFrame(Frame):

    def __init__(self, parent, cb=lambda: None):
        Frame.__init__(self, parent)
        self.parent = parent
        self.cb = cb

        self._init_ui()

    def _cb(self, *args):
        self.cb(SNAP_DICT[self._var.get()])

    def _init_ui(self):
        self._var = StringVar()

        self._snap_combobox = Combobox(self, values=SNAP_DICT.keys(),
            width=5, state='readonly')
        self._snap_combobox.config(textvariable=self._var)
        self._snap_combobox.set(SNAP_DICT.keys()[0])
        self._var.trace('w', self._cb)

        self._snap_label = Label(self, text='Snap')

        self._snap_label.pack(side=LEFT)
        self._snap_combobox.pack(side=LEFT)
