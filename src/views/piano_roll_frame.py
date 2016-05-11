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
        self._hbar = AutoScrollbar(self, orient=HORIZONTAL)
        self._vbar = AutoScrollbar(self, orient=VERTICAL)

        self._ruler_canvas = RulerCanvas(self, self._grid.get_state(),
            xscrollcommand=self._hbar.set)
        self._keyboard_canvas = KeyboardCanvas(self, self._grid.get_state(),
            yscrollcommand=self._vbar.set)
        self._grid_canvas = GridCanvas(self, self._grid.get_state(),
            xscrollcommand=self._hbar.set,
            yscrollcommand=self._vbar.set)

        self._grid.register_listener(self._keyboard_canvas.on_update)
        self._grid.register_listener(self._ruler_canvas.on_update)
        self._grid.register_listener(self._grid_canvas.on_update)

        self._hbar.config(command=self._xview)
        self._vbar.config(command=self._yview)

        self._hbar.grid(row=2, column=0, columnspan=3, sticky=E+W)
        self._vbar.grid(row=0, column=2, sticky=N+S, rowspan=3)
        self._keyboard_canvas.grid(row=1, column=0, sticky=W+N+E+S,
            padx=8, pady=(0, 8))
        self._ruler_canvas.grid(row=0, column=1, sticky=W+N+E+S,
            padx=(0, 8), pady=8)
        self._grid_canvas.grid(row=1, column=1, sticky=W+N+E+S,
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
        self._grid_canvas.select_notes(GridCanvas.ALL)
        self.parent.set_toolbox_tool(GridCanvas.SEL_TOOL)

    def _on_delete(self, event):
        self._grid_canvas.remove_notes(GridCanvas.SELECTED)

    def _on_ctrl_num(self, event):
        ctrl_pressed = event.state & PianoRollFrame.CTRL_MASK == PianoRollFrame.CTRL_MASK
        if ctrl_pressed:
            self.parent.set_toolbox_tool(int(event.keysym) - 1)

    def _xview(self, *args):
        self._ruler_canvas.xview(*args)
        self._grid_canvas.xview(*args)

    def _yview(self, *args):
        self._keyboard_canvas.yview(*args)
        self._grid_canvas.yview(*args)

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

    def set_tool(self, value):
        self._grid_canvas.set_tool(value)