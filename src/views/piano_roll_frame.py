from tkinter import *
from .ruler_canvas import RulerCanvas
from .keyboard_canvas import KeyboardCanvas
from .grid_canvas import GridCanvas
from .mousepos_frame import MousePosFrame
from include.auto_scrollbar import AutoScrollbar
from include.with_border import WithBorder
from ..grid import Grid
from ..helper import dummy


class PianoRollFrame(Frame):

    CTRL_MASK = 0x0004

    COLOR_BORDER_DEFAULT = "#000000"
    COLOR_BORDER_SELECTED = "#3399FF"

    def __init__(self, parent, dirty_cb, **kwargs):
        Frame.__init__(self, parent, **kwargs)
        self.parent = parent
        self._on_state_change = dirty_cb

        self._init_data()
        self._init_ui(dirty_cb)
        self._bind_event_handlers()

    def _init_data(self):
        self._grid = Grid()

    def _init_ui(self, dirty_cb):
        self.hbar = AutoScrollbar(self, orient=HORIZONTAL)
        self.vbar = AutoScrollbar(self, orient=VERTICAL)

        gstate = self._grid.get_state()
        self.mousepos_frame = WithBorder(
            self, MousePosFrame, gstate, borderwidth=2, padding=3,
            bordercolordefault=PianoRollFrame.COLOR_BORDER_DEFAULT,
            bordercolorselected=PianoRollFrame.COLOR_BORDER_SELECTED)
        self.ruler_canvas = WithBorder(
            self, RulerCanvas, gstate, borderwidth=2, padding=3,
            bordercolordefault=PianoRollFrame.COLOR_BORDER_DEFAULT,
            bordercolorselected=PianoRollFrame.COLOR_BORDER_SELECTED,
            xscrollcommand=self.hbar.set)
        self.keyboard_canvas = WithBorder(
            self, KeyboardCanvas, gstate, borderwidth=2, padding=3,
            bordercolordefault=PianoRollFrame.COLOR_BORDER_DEFAULT,
            bordercolorselected=PianoRollFrame.COLOR_BORDER_SELECTED,
            yscrollcommand=self.vbar.set)

        callbacks = {
            'mousepos': self._on_mouse_motion,
            'dirty': dirty_cb,
        }

        self.grid_canvas = WithBorder(
            self, GridCanvas, gstate, callbacks, borderwidth=2, padding=3,
            bordercolordefault=PianoRollFrame.COLOR_BORDER_DEFAULT,
            bordercolorselected=PianoRollFrame.COLOR_BORDER_SELECTED,
            xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)

        self._grid.register_listener(self.mousepos_frame.on_update)
        self._grid.register_listener(self.keyboard_canvas.on_update)
        self._grid.register_listener(self.ruler_canvas.on_update)
        self._grid.register_listener(self.grid_canvas.on_update)

        self.hbar.config(command=self._xview)
        self.vbar.config(command=self._yview)

        self.mousepos_frame.grid(row=0, column=0, sticky=W+N+E+S,
            padx=8, pady=8)
        self.ruler_canvas.grid(row=0, column=1, sticky=W+N+E+S,
            padx=(0, 8), pady=8)
        self.keyboard_canvas.grid(row=1, column=0, sticky=W+N+E+S,
            padx=8, pady=(0, 8))
        self.grid_canvas.grid(row=1, column=1, sticky=W+N+E+S,
            padx=(0, 8), pady=(0, 8))

        self.hbar.grid(row=2, column=0, columnspan=3, sticky=E+W)
        self.vbar.grid(row=0, column=2, sticky=N+S, rowspan=2)

        self.grid_rowconfigure(1, weight=2)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.focus_set()

    def _bind_event_handlers(self):
        self.bind_all('1', self._on_ctrl_num)
        self.bind_all('2', self._on_ctrl_num)
        self.bind_all('3', self._on_ctrl_num)

    def _on_ctrl_num(self, event):
        ctrl_pressed = (event.state & PianoRollFrame.CTRL_MASK ==
            PianoRollFrame.CTRL_MASK)
        if ctrl_pressed:
            self.parent.set_toolbox_tool(int(event.keysym) - 1)

    def _on_mouse_motion(self, x, y):
        self.mousepos_frame.set_mousepos(x, y)

    def _xview(self, *args):
        self.ruler_canvas.xview(*args)
        self.grid_canvas.xview(*args)

    def _yview(self, *args):
        self.keyboard_canvas.yview(*args)
        self.grid_canvas.yview(*args)

    def setup(self, notes):
        self.grid_canvas.remove_notes(GridCanvas.ALL)
        for note in notes:
            self.grid_canvas.add_note(note)

    def get_song_state(self):
        timesig = (self._grid.beat_count, self._grid.beat_unit)
        return {
            'notes': self.grid_canvas.note_list.notes,
            'length': self._grid.length,
            'timesig': timesig
        }

    def set_subdiv(self, value):
        if self._grid.subdiv != value:
            self._grid.subdiv = value

    def set_zoomx(self, value):
        if self._grid.zoomx != value:
            self._grid.zoomx = value

    def set_zoomy(self, value):
        if self._grid.zoomy != value:
            self._grid.zoomy = value

    def set_length(self, value):
        if self._grid.length != value:
            self._grid.length = value
            self._on_state_change()

    def set_timesig(self, timesig):
        beat_count, beat_unit = timesig
        if (self._grid.beat_count != beat_count or
            self._grid.beat_unit != beat_unit):
            self._grid.beat_count = beat_count
            self._grid.beat_unit = beat_unit
            self._on_state_change()
