from Tkinter import *
from zoomx_frame import ZoomXFrame
from zoomy_frame import ZoomYFrame


class ZoomFrame(Frame):

    def __init__(self, parent, zoomx_cb=lambda: None, zoomy_cb=lambda: None):
        Frame.__init__(self, parent)
        self.parent = parent

        self._init_ui(zoomx_cb, zoomy_cb)

    def _init_ui(self, zoomx_cb, zoomy_cb):
        self.zoomx_frame = ZoomXFrame(self, zoomx_cb)
        self.zoomy_frame = ZoomYFrame(self, zoomy_cb)

        self.zoomx_frame.pack(side=LEFT)
        self.zoomy_frame.pack(side=LEFT)