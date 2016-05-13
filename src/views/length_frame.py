from Tkinter import *
from include.custom_spinbox import CustomSpinbox
from sys import maxsize


class LengthFrame(LabelFrame):

    SPINBOX_WIDTH = 5

    def __init__(self, parent, cb=lambda *args: None):
        LabelFrame.__init__(self, parent, text="Length", padx=4, pady=4)
        self.parent = parent
        self._cb = cb

        self._init_ui()

    def _init_ui(self):
        self._bar_spinbox = CustomSpinbox(self, from_=1, to=maxsize,
            width=LengthFrame.SPINBOX_WIDTH)
        self._bar_spinbox.set('2')
        self._bar_spinbox.on_value_change(self._forward)

        self._beat_spinbox = CustomSpinbox(self, from_=1, to=4,
            width=LengthFrame.SPINBOX_WIDTH)
        self._beat_spinbox.on_value_change(self._forward)

        self._tick_spinbox = CustomSpinbox(self, from_=0, to=127,
            width=LengthFrame.SPINBOX_WIDTH)
        self._tick_spinbox.on_value_change(self._forward)

        self.after_idle(Widget.nametowidget(self._beat_spinbox,
            str(self._beat_spinbox)).config, {'validate': 'key'})
        self.after_idle(Widget.nametowidget(self._tick_spinbox,
            str(self._tick_spinbox)).config, {'validate': 'key'})

        self._bar_label = Label(self, text="Bar")
        self._beat_label = Label(self, text="Beat")
        self._tick_label = Label(self, text="Tick")

        self._bar_label.pack(side=LEFT)
        self._bar_spinbox.pack(side=LEFT)
        self._beat_label.pack(side=LEFT)
        self._beat_spinbox.pack(side=LEFT)
        self._tick_label.pack(side=LEFT)
        self._tick_spinbox.pack(side=LEFT)

    def _forward(self):
        bar = int(self._bar_spinbox.get())
        beat = int(self._beat_spinbox.get())
        tick = int(self._tick_spinbox.get())
        self._cb((bar, beat, tick))

    def set_max_beat(self, value):
        self._beat_spinbox.set_to(value)