from Tkinter import *
from ttk import Separator
from snap_frame import SnapFrame
from toolbox import Toolbox
from note_edit_frame import NoteEditFrame


class Toolbar(Frame):

    def __init__(self, parent, callbacks):
        Frame.__init__(self, parent, padx=4, pady=4)
        self.parent = parent

        self._init_ui(callbacks)

    def _init_ui(self, callbacks):
        self.snap_frame = SnapFrame(self, callbacks['snap'])
        self.toolbox = Toolbox(self, callbacks['tool'])
        self.note_data_frame = NoteEditFrame(
            self, callbacks['note'])
        self.separator = Separator(self, orient=VERTICAL)

        self.snap_frame.pack(side=LEFT)
        self.toolbox.pack(side=LEFT, padx=10)
        self.separator.pack(side=LEFT, fill=Y)
        self.note_data_frame.pack(side=LEFT, padx=10)

    def set_tool(self, value):
        self.toolbox.set(value)
