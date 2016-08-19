from Tkinter import *
from src.observables.piano_roll_observable import (OBS_GRID,
    OBS_CURSOR)
from mousepos_frame import MousePosFrame
from ruler_canvas import RulerCanvas
from keyboard_canvas import KeyboardCanvas
from grid_canvas import GridCanvas
from scrollbar_frame import ScrollbarFrame
from include.with_border import WithBorder
from src.const import (COLOR_BORDER_DEFAULT,
    COLOR_BORDER_SELECTED, ZOOM_X_VALUES,
    ZOOM_Y_VALUES)


class MainFrame(Frame):

    CTRL_MASK = 0b100

    def __init__(self, parent, **kwargs):
        Frame.__init__(self, parent, **kwargs)
        self.parent = parent

        self._init_data()
        self._init_ui()

    def _init_data(self):
        self._zoom = [1, 0.5]

    def _init_ui(self):
        self.hbar_frame = ScrollbarFrame(self, HORIZONTAL)
        self.hbar_frame.on_bttn_pressed(self._on_horizontal_zoom)
        self.vbar_frame = ScrollbarFrame(self, VERTICAL)
        self.vbar_frame.on_bttn_pressed(self._on_vertical_zoom)

        self.mousepos_frame = WithBorder(
            self, MousePosFrame, borderwidth=2, padding=3,
            bordercolordefault=COLOR_BORDER_DEFAULT)
        self.ruler_canvas = WithBorder(
            self, RulerCanvas, borderwidth=2, padding=3,
            xscrollcommand=self.hbar_frame.scrollbar.set,
            bordercolordefault=COLOR_BORDER_DEFAULT)
        self.keyboard_canvas = WithBorder(
            self, KeyboardCanvas, borderwidth=2, padding=3,
            yscrollcommand=self.vbar_frame.scrollbar.set,
            bordercolordefault=COLOR_BORDER_DEFAULT)

        grid_canvas_callbacks = {
            'mouse_pos': self._on_mouse_motion
        }

        self.grid_canvas = WithBorder(
            self, GridCanvas, grid_canvas_callbacks,
            borderwidth=2, padding=3,
            xscrollcommand=self.hbar_frame.scrollbar.set,
            yscrollcommand=self.vbar_frame.scrollbar.set,
            bordercolordefault=COLOR_BORDER_DEFAULT,
            bordercolorselected=COLOR_BORDER_SELECTED)

        self.hbar_frame.scrollbar.config(command=self._xview)
        self.vbar_frame.scrollbar.config(command=self._yview)

        self.grid_canvas.register_observer(
            self.mousepos_frame.on_state_change, OBS_GRID)
        self.grid_canvas.register_observer(
            self.keyboard_canvas.on_state_change, OBS_GRID)
        self.grid_canvas.register_observer(
            self.ruler_canvas.on_grid_change, OBS_GRID)
        self.grid_canvas.register_observer(
            self.ruler_canvas.on_cursor_change, OBS_CURSOR)

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

    def _on_mouse_motion(self, x, y):
        self.mousepos_frame.set_mousepos(x, y)

    def _on_horizontal_zoom(self, direction):
        num_of_opts = len(ZOOM_X_VALUES)
        zoomx_index = ZOOM_X_VALUES.index(self._zoom[0])

        if direction:
            min_index = min(zoomx_index + 1, num_of_opts - 1)
            self._zoom[0] = ZOOM_X_VALUES[min_index]
        else:
            max_index = max(zoomx_index - 1, 0)
            self._zoom[0] = ZOOM_X_VALUES[max_index]

        self.grid_canvas.set_zoom(self._zoom)

    def _on_vertical_zoom(self, direction):
        num_of_opts = len(ZOOM_Y_VALUES)
        zoomy_index = ZOOM_Y_VALUES.index(self._zoom[1])

        if direction:
            min_index = min(zoomy_index + 1, num_of_opts - 1)
            self._zoom[1] = ZOOM_Y_VALUES[min_index]
        else:
            max_index = max(zoomy_index - 1, 0)
            self._zoom[1] = ZOOM_Y_VALUES[max_index]

        self.grid_canvas.set_zoom(self._zoom)

    def _xview(self, *args):
        self.ruler_canvas.xview(*args)
        self.grid_canvas.xview(*args)

    def _yview(self, *args):
        self.keyboard_canvas.yview(*args)
        self.grid_canvas.yview(*args)