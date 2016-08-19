from Tkinter import *
from src.models.grid_model import GridModel
from include.custom_canvas import CustomCanvas
from src.helper import to_pitchname, to_notedur, px_to_tick


class MousePosFrame(Frame):

    CANVAS_WIDTH = 100
    CANVAS_HEIGHT = 45

    def __init__(self, parent):
        Frame.__init__(self, parent)

        self._init_data()
        self._init_ui()
        self._bind_event_handlers()

    def _init_data(self):
        self._grid_state = GridModel()
        self._mouse_pos = (0, 0)

    def _init_ui(self):
        self.canvas = CustomCanvas(
            self, width=MousePosFrame.CANVAS_WIDTH,
            height=MousePosFrame.CANVAS_HEIGHT,
            bg='white')
        self.canvas.pack()

        self.set_mousepos(*self._mouse_pos)

    def _bind_event_handlers(self):
        self.canvas.bind('<ButtonPress-1>', self._on_bttnone_press)

    def _draw(self):
        self._draw_text()
        self._draw_line()

    def _draw_text(self):
        grid_height = self._grid_state.height()
        cell_height = self._grid_state.cell_height()
        beat_count, beat_unit = self._grid_state.timesig
        zoomx = self._grid_state.zoom[0]

        x, y = self._mouse_pos
        pos = to_notedur(
            px_to_tick(x / zoomx), beat_count, beat_unit)
        pos[0] += 1
        pos[1] += 1

        midinumber = int((grid_height - y - 1) / cell_height)
        pitchname = to_pitchname(midinumber)

        id = self.canvas.add_to_layer(
            0, self.canvas.create_text, (0, 3),
            text="{0}.{1}.{2}".format(*pos),
            anchor=NW)
        offset = self._calc_offset(id)
        self.canvas.move(id, offset, 0)

        id = self.canvas.add_to_layer(
            0, self.canvas.create_text, (0, 27),
            text=pitchname, anchor=NW)
        offset = self._calc_offset(id)
        self.canvas.move(id, offset, 0)

    def _draw_line(self):
        x1 = 0
        x2 = MousePosFrame.CANVAS_WIDTH
        y = MousePosFrame.CANVAS_HEIGHT / 2
        self.canvas.add_to_layer(
            0, self.canvas.create_line, (x1, y, x2, y))

    def _calc_offset(self, id):
        coords = self.canvas.bbox(id)
        return ((MousePosFrame.CANVAS_WIDTH / 2) -
            ((coords[2] - coords[0]) / 2))

    def _on_bttnone_press(self, event):
        self.focus_set()

    def set_mousepos(self, x, y):
        self._mouse_pos = (x, y)
        self.canvas.delete(ALL)
        self._draw()

    def on_state_change(self, new_grid_state):
        self._grid_state = new_grid_state


