from Tkinter import *
from zoomx_frame import ZoomXFrame
from zoomy_frame import ZoomYFrame
from ..helper import dummy

class ZoomFrame(Frame):

    def __init__(self, parent, callbacks):
        Frame.__init__(self, parent)
        self.parent = parent

        self._init_ui(callbacks)

    def _init_ui(self, callbacks):
        self.zoomx_frame = ZoomXFrame(
            self, callbacks.get('zoomx', dummy))
        self.zoomy_frame = ZoomYFrame(
            self, callbacks.get('zoomy', dummy))

        self.zoomx_frame.pack(side=LEFT)
        self.zoomy_frame.pack(side=LEFT)