from Tkinter import *


class LengthFrame(Frame):

    SPINBOX_WIDTH = 5

    def __init__(self, parent, cb):
        Frame.__init__(self, parent)
        self.parent = parent
        self.cb = cb

        self._init_ui()

    def _cb(self, *args):
        bar = int(self._bar_var.get())
        beat = int(self._beat_var.get())
        tick = int(self._tick_var.get())
        self.cb(bar, beat, tick)

    def _init_ui(self):
        self._bar_var = StringVar()
        self._beat_var = StringVar()
        self._tick_var = StringVar()

        self._bar_spinbox = Spinbox(self, from_=1, to=99999,
            textvariable=self._bar_var, width=LengthFrame.SPINBOX_WIDTH)
        self._beat_spinbox = Spinbox(self, from_=1, to=4,
            textvariable=self._beat_var, width=LengthFrame.SPINBOX_WIDTH)
        self._tick_spinbox = Spinbox(self, from_=0, to=63,
            textvariable=self._tick_var, width=LengthFrame.SPINBOX_WIDTH)
        self._bar_var.set('2')

        self._bar_var.trace("w", self._cb)
        self._beat_var.trace("w", self._cb)
        self._tick_var.trace("w", self._cb)

        self._bar_label = Label(self, text="Bar")
        self._beat_label = Label(self, text="Beat")
        self._tick_label = Label(self, text="Tick")

        self._bar_label.pack(side=LEFT)
        self._bar_spinbox.pack(side=LEFT)
        self._beat_label.pack(side=LEFT)
        self._beat_spinbox.pack(side=LEFT)
        self._tick_label.pack(side=LEFT)
        self._tick_spinbox.pack(side=LEFT)