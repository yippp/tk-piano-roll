from Tkinter import *
from include.custom_spinbox import CustomSpinbox
from src.helper import to_pitchname, to_midinumber
from src.const import PITCHNAMES


class PitchFrame(Frame):

    def __init__(self, parent, cb):
        Frame.__init__(self, parent)
        self.parent = parent
        self._cb = cb

        self._init_ui()

    def _init_ui(self):
        self.pitch_label = Label(self, text='Pitch')

        values = ["{0}{1}".format(PITCHNAMES[i % 12],
            int(i / 12) - 2) for i in range(128)]
        self.pitch_spinbox = CustomSpinbox(
            self, callback=self._forward, values=values,
            start='C4', width=4, match_case=False,
            convert=1)

        self.pitch_label.pack(side=LEFT)
        self.pitch_spinbox.pack(side=LEFT)

    def _forward(self):
        midinumber = to_midinumber(self.pitch_spinbox.get())
        self._cb('midinumber', midinumber)

    def set_pitch(self, pitch):
        pitchname = to_pitchname(pitch)
        self.pitch_spinbox.set(pitchname)