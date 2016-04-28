from Tkinter import *
from length_frame import LengthFrame

class BottomBar(Frame):

    def __init__(self, parent, len_cb):
        Frame.__init__(self, parent, padx=4, pady=4)
        self.parent = parent

        self._init_ui(len_cb)

    def _init_ui(self, len_cb):
        self._length_frame = LengthFrame(self, len_cb)
        self._length_frame.pack(side=LEFT)