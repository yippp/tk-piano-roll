from Tkinter import *
from end_frame import EndFrame
from timesig_frame import TimeSigFrame


class BottomBar(Frame):

    def __init__(self, parent, callbacks):
        Frame.__init__(self, parent, padx=4, pady=4)
        self.parent = parent

        self._init_ui(callbacks)

    def _init_ui(self, callbacks):
        self.timesig_frame = TimeSigFrame(self, callbacks['timesig'])
        self.end_frame = EndFrame(self, callbacks['end'])

        self.timesig_frame.grid(row=0, column=0, sticky=W)
        self.end_frame.grid(row=0, column=2, sticky=E)
        self.grid_columnconfigure(0, weight=1)

    def set_end(self, end):
        self.end_frame.set_end(end)

    def set_timesig(self, timesig):
        self.timesig_frame.set_timesig(timesig)

    def set_max_beat(self, max_beat):
        self.end_frame.set_max_beat(max_beat)

    def set_max_tick(self, max_tick):
        self.end_frame.set_max_tick(max_tick)