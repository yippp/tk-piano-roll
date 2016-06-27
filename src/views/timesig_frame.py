from Tkinter import *
from ttk import Combobox
from include.custom_spinbox import CustomSpinbox
from src.helper import dummy


class TimeSigFrame(LabelFrame):

    def __init__(self, parent, cb=dummy):
        LabelFrame.__init__(self, parent)
        self.cb = cb

        self._init_ui()

    def _init_ui(self):
        self.config(text="Time Signature", padx=4, pady=5)

        self.beat_count_spinbox = CustomSpinbox(
            self, self._forward, start=4, from_=1,
            to=99, width=3)

        self._beat_unit_var = StringVar()
        values = [str(2 ** i) for i in range(1, 6)]
        self.beat_unit_combobox = Combobox(
            self, values=values, width=3,
            textvariable=self._beat_unit_var,
            state='readonly')
        self._beat_unit_var.set('4')
        self._beat_unit_var.trace('w', self._forward)

        self.sep_label = Label(self, text='/')

        self.beat_count_spinbox.grid(row=0, column=0, sticky=W)
        self.sep_label.grid(row=0, column=1, sticky=W+N+E+S)
        self.beat_unit_combobox.grid(row=0, column=2, sticky=E)
        self.grid_columnconfigure(1, weight=1)

    def _forward(self, *args):
        beat_count = int(self.beat_count_spinbox.get())
        beat_unit = int(self.beat_unit_combobox.get())
        self.cb((beat_count, beat_unit))

    def set_timesig(self, timesig):
        beat_count, beat_unit = timesig
        self.beat_count_spinbox.set(beat_count)
        self.beat_unit_combobox.set(beat_unit)