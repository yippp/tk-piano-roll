from Tkinter import *
from piano_roll_frame import PianoRollFrame
from toolbar import Toolbar
from bottombar import BottomBar


class PianoRoll(Frame):

    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.parent = parent
        self._init_ui()

    def _init_ui(self):
        callbacks = {
            'snap': self.set_snap,
            'zoomx': self.set_zoomx,
            'zoomy': self.set_zoomy,
            'tool': self.set_canvas_tool
        }

        self._toolbar = Toolbar(self, callbacks)
        self._piano_roll_frame = PianoRollFrame(self)
        self._bottombar = BottomBar(self, self.set_length)

        self._toolbar.pack(side=TOP, fill=X)
        self._piano_roll_frame.pack(fill=BOTH, expand=True)
        self._bottombar.pack(side=BOTTOM, fill=X)
        self.pack(fill=BOTH, expand=True)

    def set_snap(self, snap_value):
        self._piano_roll_frame.set_subdiv(snap_value)

    def set_zoomx(self, value):
        self._piano_roll_frame.set_zoomx(value)

    def set_zoomy(self, value):
        self._piano_roll_frame.set_zoomy(value)

    def set_length(self, bar, beat, tick):
        from ..helper import to_ticks
        self._piano_roll_frame.set_length(to_ticks(bar, beat, tick))

    def set_canvas_tool(self, tool):
        self._piano_roll_frame.set_tool(tool)

    def set_toolbox_tool(self, value):
        self._toolbar.set_tool(value)