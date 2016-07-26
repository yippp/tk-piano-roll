from Tkinter import *
from mousepos_frame import MousePosFrame
from ruler_canvas import RulerCanvas
from keyboard_canvas import KeyboardCanvas
from grid_canvas import GridCanvas
from scrollbar_frame import ScrollbarFrame
from include.with_border import WithBorder
from src.grid import Grid
from src.const import COLOR_BORDER_DEFAULT, COLOR_BORDER_SELECTED


class MainFrame(Frame):

    CTRL_MASK = 0x0004

    def __init__(self, parent, callbacks, **kwargs):
        Frame.__init__(self, parent, **kwargs)
        self.parent = parent

        self._init_data(callbacks)
        self._init_ui()
        self._bind_event_handlers()

    def _init_data(self, callbacks):
        self._grid = Grid()
        self._callbacks = callbacks

    def _init_ui(self):
        self.hbar_frame = ScrollbarFrame(
            self, HORIZONTAL,
            self._callbacks.get('zoomx'))
        self.vbar_frame = ScrollbarFrame(
            self, VERTICAL,
            self._callbacks.get('zoomy'))

        gstate = self._grid.get_state()
        self.mousepos_frame = WithBorder(
            self, MousePosFrame, gstate, borderwidth=2, padding=3,
            bordercolordefault=COLOR_BORDER_DEFAULT)
        self.ruler_canvas = WithBorder(
            self, RulerCanvas, gstate, borderwidth=2, padding=3,
            xscrollcommand=self.hbar_frame.scrollbar.set,
            bordercolordefault=COLOR_BORDER_DEFAULT)
        self.keyboard_canvas = WithBorder(
            self, KeyboardCanvas, gstate, borderwidth=2, padding=3,
            yscrollcommand=self.vbar_frame.scrollbar.set,
            bordercolordefault=COLOR_BORDER_DEFAULT)

        grid_canvas_callbacks = {
            'note': self._callbacks['note'],
            'dirty': self._callbacks['dirty'],
            'mouse_pos': self._on_mouse_motion,
            'play_pos': self._on_play_pos_change
        }

        self.grid_canvas = WithBorder(
            self, GridCanvas, gstate, grid_canvas_callbacks,
            borderwidth=2, padding=3,
            xscrollcommand=self.hbar_frame.scrollbar.set,
            yscrollcommand=self.vbar_frame.scrollbar.set,
            bordercolordefault=COLOR_BORDER_DEFAULT,
            bordercolorselected=COLOR_BORDER_SELECTED)

        self.hbar_frame.scrollbar.config(command=self._xview)
        self.vbar_frame.scrollbar.config(command=self._yview)

        self._grid.register_listener(self.mousepos_frame.on_update)
        self._grid.register_listener(self.keyboard_canvas.on_update)
        self._grid.register_listener(self.ruler_canvas.on_update)
        self._grid.register_listener(self.grid_canvas.on_update)

        self.mousepos_frame.grid(row=0, column=0,
            sticky=W+N+E+S, padx=8, pady=8)
        self.ruler_canvas.grid(row=0, column=1,
            sticky=W+N+E+S, padx=(0, 8), pady=8)
        self.keyboard_canvas.grid(row=1, column=0,
            sticky=W+N+E+S, padx=8, pady=(0, 8))
        self.grid_canvas.grid(row=1, column=1,
            sticky=W+N+E+S, padx=(0, 8), pady=(0, 8))

        self.vbar_frame.grid(
            row=0, column=2, rowspan=2, sticky=N+S, pady=8)
        self.hbar_frame.grid(
            row=2, column=0, columnspan=2, sticky=E+W, padx=8)

        self.grid_rowconfigure(1, weight=2)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.focus_set()

    def _bind_event_handlers(self):
        self.bind_all('1', self._on_ctrl_num)
        self.bind_all('2', self._on_ctrl_num)
        self.bind_all('3', self._on_ctrl_num)

    def _on_ctrl_num(self, event):
        ctrl_pressed = (event.state & MainFrame.CTRL_MASK ==
            MainFrame.CTRL_MASK)
        if ctrl_pressed:
            self._callbacks['tool'](int(event.keysym) - 1)

    def _on_mouse_motion(self, x, y):
        self.mousepos_frame.set_mousepos(x, y)

    def _on_play_pos_change(self, ticks):
        self.grid_canvas.set_play_pos(ticks)
        self.ruler_canvas.set_play_pos(ticks)

    def _xview(self, *args):
        self.ruler_canvas.xview(*args)
        self.grid_canvas.xview(*args)

    def _yview(self, *args):
        self.keyboard_canvas.yview(*args)
        self.grid_canvas.yview(*args)

    def setup(self, notes):
        self.grid_canvas.remove_note(GridCanvas.ALL)
        for note in notes:
            self.grid_canvas.add_note(note)

    def get_song_state(self):
        timesig = (self._grid.beat_count, self._grid.beat_unit)
        return {
            'notes': self.grid_canvas.note_list.notes,
            'end': self._grid.end,
            'timesig': timesig
        }

    def set_subdiv(self, subdiv):
        if self._grid.subdiv != subdiv:
            self._grid.subdiv = subdiv

    def set_zoomx(self, zoomx):
        if self._grid.zoomx != zoomx:
            self._grid.zoomx = zoomx

    def set_zoomy(self, zoomy):
        if self._grid.zoomy != zoomy:
            self._grid.zoomy = zoomy

    def set_end(self, end):
        if self._grid.end != end:
            self._grid.end = end

            dirty_cb = self._callbacks.get('dirty')
            if dirty_cb: dirty_cb(True)

    def set_timesig(self, timesig):
        beat_count, beat_unit = timesig
        if (self._grid.beat_count != beat_count or
            self._grid.beat_unit != beat_unit):
            self._grid.beat_count = beat_count
            self._grid.beat_unit = beat_unit

            dirty_cb = self._callbacks.get('dirty')
            if dirty_cb: dirty_cb(True)