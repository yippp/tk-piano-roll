from Tkinter import *
from length_frame import LengthFrame
from timesig_frame import TimeSigFrame


class BottomBar(Frame):

    def __init__(self, parent, callbacks):
        Frame.__init__(self, parent, padx=4, pady=4)
        self.parent = parent

        self._init_ui(callbacks)

    def _init_ui(self, callbacks):
        self.timesig_frame = TimeSigFrame(self, callbacks['timesig'])
        self.length_frame = LengthFrame(self, callbacks['length'])

        self.timesig_frame.grid(row=0, column=0, sticky=W)
        self.length_frame.grid(row=0, column=2, sticky=E)
        self.grid_columnconfigure(0, weight=1)

    def set_length(self, length):
        self.length_frame.set_length(length)

    def set_timesig(self, timesig):
        self.timesig_frame.set_timesig(timesig)

    def set_max_beat_count(self, value):
        self.length_frame.set_max_beat(value)
