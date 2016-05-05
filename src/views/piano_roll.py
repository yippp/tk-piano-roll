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
        toolbar_callbacks = {
            'snap': self.set_snap,
            'zoomx': self.set_zoomx,
            'zoomy': self.set_zoomy,
            'tool': self.set_canvas_tool
        }

        bottombar_callbacks = {
            'length': self.set_length,
            'timesig': self.set_timesig
        }

        self._toolbar = Toolbar(self, toolbar_callbacks)
        self._piano_roll_frame = PianoRollFrame(self)
        self._bottombar = BottomBar(self, bottombar_callbacks)

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

    def set_length(self, length):
        self._piano_roll_frame.set_length(length)

    def set_canvas_tool(self, tool):
        self._piano_roll_frame.set_tool(tool)

    def set_toolbox_tool(self, value):
        self._toolbar.set_tool(value)

    def set_timesig(self, beat_count, beat_unit):
        self._piano_roll_frame.set_timesig(beat_count, beat_unit)