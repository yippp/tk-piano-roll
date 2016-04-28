from Tkinter import *
from snap_frame import SnapFrame
from zoom_frame import ZoomFrame
from toolbox import Toolbox

class Toolbar(Frame):

    def __init__(self, parent, callbacks):
        Frame.__init__(self, parent, padx=4, pady=4)
        self.parent = parent

        self._init_ui(callbacks)

    def _init_ui(self, callbacks):
        self._snap_frame = SnapFrame(self, callbacks['snap'])
        self._zoom_frame = ZoomFrame(self, callbacks['zoomx'], callbacks['zoomy'])
        self._toolbox = Toolbox(self, callbacks['tool'])

        self._snap_frame.pack(side=LEFT)
        self._toolbox.pack(side=LEFT)
        self._zoom_frame.pack(side=RIGHT)

