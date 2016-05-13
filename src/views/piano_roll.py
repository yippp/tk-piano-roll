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

    def _init_ui(self):
        root = self._root()
        menu = PianoRollMenu(root, saveas_cmd=self._saveas_cmd)
        root.config(menu=menu)

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

        self.toolbar = Toolbar(self, toolbar_callbacks)
        self.piano_roll_frame = PianoRollFrame(self)
        self.bottombar = BottomBar(self, bottombar_callbacks)

        self.toolbar.pack(side=TOP, fill=X)
        self.piano_roll_frame.pack(fill=BOTH, expand=True)
        self.bottombar.pack(side=BOTTOM, fill=X)
        self.pack(fill=BOTH, expand=True)

    def _saveas_cmd(self):
        from tkFileDialog import asksaveasfilename
        from ..helper import calc_ticks_per_bar, to_notedur
        from ..const import SIXTEENTH_UNIT_WIDTH_IN_PX, CELL_HEIGHT_IN_PX

        filename = asksaveasfilename(parent=self)
        if not filename: return
        file = open(filename, 'w')

        data = self.piano_roll_frame.get_song_data()
        note_list = data['note_list']
        beat_count = data['beat_count']
        beat_unit = data['beat_unit']
        length = data['length']

        file.write("{0} {1} {2};\n".format(*[str(x) for x in length]))
        for note in note_list:
            note_left = note.rect[0]
            note_top = note.rect[1]

            grid_height = CELL_HEIGHT_IN_PX * 128
            midinumber = int((grid_height - note_top) / CELL_HEIGHT_IN_PX) - 1

            ratio = 16.0 / SIXTEENTH_UNIT_WIDTH_IN_PX
            ticks = int(note_left * ratio)
            ticks_per_bar = calc_ticks_per_bar(16, beat_count, beat_unit)
            pos = to_notedur(ticks, ticks_per_bar, beat_count)
            pos[0] += 1
            pos[1] += 1

            duration = int(ticks_per_bar / (note.rect[2] * ratio))
            file.write("{0} | 100 | {1} {2} {3} | {4};\n".format(midinumber,
                pos[0], pos[1], pos[2], duration))

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
