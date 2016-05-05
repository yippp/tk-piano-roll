from Tkinter import *
from ttk import Combobox


class TimeSigFrame(LabelFrame):

    def __init__(self, parent, cb=lambda bc, bu: None):
        LabelFrame.__init__(self, parent, text="Time Signature", padx=4, pady=5)
        self.cb = cb

        self._init_ui()

    def _cb(self, *args):
        beat_count = int(self._beat_count_var.get())
        beat_unit = int(self._beat_unit_var.get())
        self.cb(beat_count, beat_unit)

    def _init_ui(self):
        self._beat_count_var = StringVar()
        self._beat_unit_var = StringVar()

        self._beat_count_combobox = Spinbox(self, from_=1, to=99, width=2,
            textvariable=self._beat_count_var)
        self._beat_unit_combobox = Combobox(self, values=[str(2 ** i) for i in range(1, 6)],
            width=2, textvariable=self._beat_unit_var)
        self._sep_label = Label(self, text='/')

        self._beat_count_var.set('4')
        self._beat_count_var.trace("w", self._cb)
        self._beat_unit_var.set('4')
        self._beat_unit_var.trace("w", self._cb)

        self._beat_count_combobox.grid(row=0, column=0, sticky=W)
        self._sep_label.grid(row=0, column=1, sticky=W+N+E+S)
        self._beat_unit_combobox.grid(row=0, column=2, sticky=E)
        self.grid_columnconfigure(1, weight=1)