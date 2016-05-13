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
        self.bar_spinbox = CustomSpinbox(self, from_=1, to=maxsize,
            width=LengthFrame.SPINBOX_WIDTH)
        self.bar_spinbox.set('2')
        self.bar_spinbox.on_value_change(self._forward)

        self.beat_spinbox = CustomSpinbox(self, from_=1, to=4,
            width=LengthFrame.SPINBOX_WIDTH)
        self.beat_spinbox.on_value_change(self._forward)

        self.tick_spinbox = CustomSpinbox(self, from_=0, to=127,
            width=LengthFrame.SPINBOX_WIDTH)
        self.tick_spinbox.on_value_change(self._forward)

        self.after_idle(Widget.nametowidget(self.beat_spinbox,
            str(self.beat_spinbox)).config, {'validate': 'key'})
        self.after_idle(Widget.nametowidget(self.tick_spinbox,
            str(self.tick_spinbox)).config, {'validate': 'key'})

        self.bar_label = Label(self, text="Bar")
        self.beat_label = Label(self, text="Beat")
        self.tick_label = Label(self, text="Tick")

        self.bar_label.pack(side=LEFT)
        self.bar_spinbox.pack(side=LEFT)
        self.beat_label.pack(side=LEFT)
        self.beat_spinbox.pack(side=LEFT)
        self.tick_label.pack(side=LEFT)
        self.tick_spinbox.pack(side=LEFT)

    def _forward(self):
        bar = int(self.bar_spinbox.get())
        beat = int(self.beat_spinbox.get())
        tick = int(self.tick_spinbox.get())
        self._cb((bar, beat, tick))

    def set_max_beat(self, value):
        self.beat_spinbox.set_to(value)