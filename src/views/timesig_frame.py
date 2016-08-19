from Tkinter import *
from include.custom_spinbox import CustomSpinbox
from src.helper import dummy


class TimeSigFrame(LabelFrame):

    def __init__(self, parent, callback=dummy):
        LabelFrame.__init__(self, parent)

        self._init_data(callback)
        self._init_ui()

    def _init_data(self, callback):
        self._cb = callback

    def _init_ui(self):
        self.config(text="Time Signature", padx=4, pady=5)

        self.beat_count_spinbox = CustomSpinbox(
            self, start=4, from_=1, to=99, width=3,
            callback=self._notify)

        values = [str(2 ** i) for i in range(1, 6)]
        self.beat_unit_spinbox = CustomSpinbox(
            self, values=values, start=4, width=3,
            callback=self._notify)

        self.sep_label = Label(self, text='/')

        self.beat_count_spinbox.grid(row=0, column=0, sticky=W)
        self.sep_label.grid(row=0, column=1, sticky=W+N+E+S)
        self.beat_unit_spinbox.grid(row=0, column=2, sticky=E)
        self.grid_columnconfigure(1, weight=1)

    def _notify(self, *args):
        beat_count = int(self.beat_count_spinbox.get())
        beat_unit = int(self.beat_unit_spinbox.get())
        self._cb((beat_count, beat_unit))

    def set_timesig(self, timesig):
        beat_count, beat_unit = timesig
        self.beat_count_spinbox.set(beat_count)
        self.beat_unit_spinbox.set(beat_unit)
