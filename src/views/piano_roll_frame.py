from Tkinter import *
from ruler_canvas import RulerCanvas
from keyboard_canvas import KeyboardCanvas
from grid_canvas import GridCanvas
from include.auto_scrollbar import AutoScrollbar
from ..grid import Grid


class PianoRollFrame(Frame):

    CTRL_MASK = 0x0004

    def __init__(self, parent, **kwargs):
        Frame.__init__(self, parent, **kwargs)
        self.parent = parent

        self._init_data()
        self._init_ui()
        self._bind_event_handlers()

    def _init_data(self):
        self._grid = Grid()

    def _init_ui(self):
        self.hbar = AutoScrollbar(self, orient=HORIZONTAL)
        self.vbar = AutoScrollbar(self, orient=VERTICAL)

        state = self._grid.get_state()
        self.ruler_canvas = RulerCanvas(self, state,
            xscrollcommand=self.hbar.set)
        self.keyboard_canvas = KeyboardCanvas(self, state,
            yscrollcommand=self.vbar.set)
        self.grid_canvas = GridCanvas(self, state,
            xscrollcommand=self.hbar.set,
            yscrollcommand=self.vbar.set)

        self._grid.register_listener(self.keyboard_canvas.on_update)
        self._grid.register_listener(self.ruler_canvas.on_update)
        self._grid.register_listener(self.grid_canvas.on_update)

        self.hbar.config(command=self._xview)
        self.vbar.config(command=self._yview)

        self.hbar.grid(row=2, column=0, columnspan=3, sticky=E+W)
        self.vbar.grid(row=0, column=2, sticky=N+S, rowspan=2)
        self.keyboard_canvas.grid(row=1, column=0, sticky=W+N+E+S,
            padx=8, pady=(0, 8))
        self.ruler_canvas.grid(row=0, column=1, sticky=W+N+E+S,
            padx=(0, 8), pady=8)
        self.grid_canvas.grid(row=1, column=1, sticky=W+N+E+S,
            padx=(0, 8), pady=(0, 8))

        self.grid_rowconfigure(1, weight=2)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.focus_set()

    def _bind_event_handlers(self):
        self.bind('<Control-a>', self._on_ctrl_a)
        self.bind('<Delete>', self._on_delete)
        self.bind('1', self._on_ctrl_num)
        self.bind('2', self._on_ctrl_num)
        self.bind('3', self._on_ctrl_num)

    def _on_ctrl_a(self, event):
        self.grid_canvas.select_notes(GridCanvas.ALL)
        self.parent.set_toolbox_tool(GridCanvas.TOOL_SEL)

    def _on_delete(self, event):
        self.grid_canvas.remove_notes(GridCanvas.SELECTED)

    def _on_ctrl_num(self, event):
        ctrl_pressed = (event.state & PianoRollFrame.CTRL_MASK ==
            PianoRollFrame.CTRL_MASK)
        if ctrl_pressed:
            self.parent.set_toolbox_tool(int(event.keysym) - 1)

    def _xview(self, *args):
        self.ruler_canvas.xview(*args)
        self.grid_canvas.xview(*args)

    def _yview(self, *args):
        self.keyboard_canvas.yview(*args)
        self.grid_canvas.yview(*args)

    def get_song_data(self):
        return {
            'note_list': self.grid_canvas.get_note_list(),
            'length': self._grid.length,
            'beat_count': self._grid.beat_count,
            'beat_unit': self._grid.beat_unit
        }

    def set_subdiv(self, value):
        self._grid.subdiv = value

    def set_zoomx(self, value):
        self._grid.zoomx = value

    def set_zoomy(self, value):
        self._grid.zoomy = value

    def set_length(self, value):
        self._grid.length = value

    def set_timesig(self, beat_count, beat_unit):
        self._grid.beat_count = beat_count
        self._grid.beat_unit = beat_unit