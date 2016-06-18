import os
from Tkinter import *
from piano_roll_menu import PianoRollMenu
from piano_roll_frame import PianoRollFrame
from toolbar import Toolbar
from bottombar import BottomBar


class PianoRoll(Frame):

    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.parent = parent

        self._init_ui()
        self._init_data()

    def _init_ui(self):
        menu_cb = {
            'open': self._open_cmd,
            'save_as': self._saveas_cmd
        }

        toolbar_cb = {
            'snap': self.set_snap,
            'zoomx': self.set_zoomx,
            'zoomy': self.set_zoomy,
            'tool': self.set_canvas_tool
        }

        bottombar_cb = {
            'length': self.set_length,
            'timesig': self.set_timesig
        }

        root = self._root()
        menu = PianoRollMenu(root, menu_cb)
        root.config(menu=menu)

        self.toolbar = Toolbar(self, toolbar_cb)
        self.piano_roll_frame = PianoRollFrame(self)
        self.bottombar = BottomBar(self, bottombar_cb)

        self.toolbar.pack(side=TOP, fill=X)
        self.piano_roll_frame.pack(fill=BOTH, expand=True)
        self.bottombar.pack(side=BOTTOM, fill=X)
        self.pack(fill=BOTH, expand=True)

    def _init_data(self):
        self._initial_dir = None

    def _open_cmd(self):
        from tkFileDialog import askopenfilename
        from ..helper import load_song

        filename = askopenfilename(parent=self,
            initialdir=self._initial_dir)
        if not filename: return

        self._initial_dir = os.path.dirname(filename)

        song_data = load_song(filename)
        self.piano_roll_frame.setup(song_data)

    def _saveas_cmd(self):
        from tkFileDialog import asksaveasfilename
        from ..helper import save_song

        filename = asksaveasfilename(parent=self,
            initialdir=self._initial_dir)
        if not filename: return

        self._initial_dir = os.path.dirname(filename)

        data = self.piano_roll_frame.get_song_data()
        save_song(filename, data)

    def set_snap(self, snap_value):
        self.piano_roll_frame.set_subdiv(snap_value)

    def set_zoomx(self, value):
        self.piano_roll_frame.set_zoomx(value)

    def set_zoomy(self, value):
        self.piano_roll_frame.set_zoomy(value)

    def set_length(self, length):
        self.piano_roll_frame.set_length(length)

    def set_canvas_tool(self, tool):
        self.piano_roll_frame.grid_canvas.set_tool(tool)

    def set_toolbox_tool(self, value):
        self.toolbar.set_tool(value)

    def set_timesig(self, beat_count, beat_unit):
        self.piano_roll_frame.set_timesig(beat_count, beat_unit)
        self.bottombar.set_max_beat(beat_count)
