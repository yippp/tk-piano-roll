from Tkinter import *
from snap_frame import SnapFrame
from toolbox import Toolbox
from velocity_frame import VelocityFrame


class Toolbar(Frame):

    def __init__(self, parent, callbacks):
        Frame.__init__(self, parent, padx=4, pady=4)
        self.parent = parent

        self._init_ui(callbacks)

    def _init_ui(self, callbacks):
        self.snap_frame = SnapFrame(self, callbacks['snap'])
        self.toolbox = Toolbox(self, callbacks['tool'])
        self.velocity_frame = VelocityFrame(
            self, callbacks['velocity'])

        self.snap_frame.pack(side=LEFT)
        self.toolbox.pack(side=LEFT, padx=10)
        self.velocity_frame.pack(side=LEFT, padx=10)

    def set_tool(self, value):
        self.toolbox.set(value)
