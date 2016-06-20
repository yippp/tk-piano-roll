from Tkinter import *
from ..helper import to_pitchname, to_notedur, px_to_tick


class MousePosFrame(Frame):

    FRAME_WIDTH = 128

    def __init__(self, parent, gstate):
        Frame.__init__(self, parent)

        self._init_data(gstate)
        self._init_ui()
        self._bind_event_handlers()

    def _init_data(self, gstate):
        self._gstate = gstate
        self._mouse_pos = (0, 0)

    def _bind_event_handlers(self):
        self._pos_label.bind(
            '<ButtonPress-1>', self._on_bttnone_press)

    def _init_ui(self):
        self.config(width=MousePosFrame.FRAME_WIDTH)

        self._pos_label = Label(self, bg='white')
        self._pos_label.pack(fill=BOTH, expand=True)

        self.set_mousepos(*self._mouse_pos)

    def _on_bttnone_press(self, event):
        self.focus_set()

    def set_mousepos(self, x, y):
        grid_height = self._gstate.height()
        cell_height = self._gstate.cell_height()
        beat_count = self._gstate.beat_count
        beat_unit = self._gstate.beat_unit
        zoomx = self._gstate.zoomx

        pos = to_notedur(
            px_to_tick(x / zoomx), beat_count, beat_unit)
        pos[0] += 1
        pos[1] += 1

        midinumber = int((grid_height - y - 1) / cell_height)
        octave = int(midinumber / 12) - 2
        pitchname = to_pitchname(midinumber)
        text = "{0}{1} / {2}.{3}.{4}".format(
            pitchname, octave, *pos)
        self._pos_label.config(text=text)
        self._mouse_pos = (x, y)

    def on_update(self, gstate):
        self._gstate = gstate
        self.set_mousepos(*self._mouse_pos)


