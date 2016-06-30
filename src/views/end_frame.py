from sys import maxsize
from Tkinter import *
from include.custom_spinbox import CustomSpinbox
from src.const import TICKS_PER_QUARTER_NOTE


class EndFrame(LabelFrame):

    SPINBOX_WIDTH = 5

    def __init__(self, parent, cb=lambda *args: None):
        LabelFrame.__init__(self, parent)
        self.parent = parent
        self._cb = cb

        self._init_ui()

    def _init_ui(self):
        self.config(text="End", padx=4, pady=4)

        self.bar_spinbox = CustomSpinbox(
            self, callback=self._forward,
            from_=1, to=maxsize, start=2,
            width=EndFrame.SPINBOX_WIDTH)

        self.beat_spinbox = CustomSpinbox(
            self, callback=self._forward,
            from_=1, to=4, width=EndFrame.SPINBOX_WIDTH)

        self.tick_spinbox = CustomSpinbox(
            self, callback=self._forward, from_=0,
            to= TICKS_PER_QUARTER_NOTE - 1,
            width=EndFrame.SPINBOX_WIDTH)

        self.after_idle(Widget.nametowidget(
            self.beat_spinbox, str(self.beat_spinbox)).config,
            {'validate': 'key'})
        self.after_idle(Widget.nametowidget(
            self.tick_spinbox, str(self.tick_spinbox)).config,
            {'validate': 'key'})

        self.bar_spinbox.pack(side=LEFT)
        self.beat_spinbox.pack(side=LEFT, padx=4)
        self.tick_spinbox.pack(side=LEFT)

    def _forward(self):
        bar = int(self.bar_spinbox.get())
        beat = int(self.beat_spinbox.get())
        tick = int(self.tick_spinbox.get())
        self._cb((bar, beat, tick))

    def set_end(self, end):
        bar, beat, tick = end
        self.bar_spinbox.set(bar)
        self.beat_spinbox.set(beat)
        self.tick_spinbox.set(tick)
        self._forward()

    def set_max_beat(self, max_beat):
        self.beat_spinbox.to = max_beat
        self._forward()

    def set_max_tick(self, max_tick):
        self.tick_spinbox.to = max_tick
        self._forward()