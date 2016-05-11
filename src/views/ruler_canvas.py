import math
from Tkinter import *
from include.custom_canvas import CustomCanvas


class RulerCanvas(CustomCanvas):

    HEIGHT = 32

    LINE_LAYER = 0
    TEXT_LAYER = 0

    NORMAL_LINE_COLOR = '#CCCCCC'
    BAR_LINE_COLOR = '#000000'

    def __init__(self, parent, gstate, **kwargs):
        CustomCanvas.__init__(self, parent, bg='white',
            bd=2, relief=SUNKEN, **kwargs)

        self._init_data(gstate)
        self._bind_event_handlers()
        self._draw()

    def _init_data(self, gstate):
        self._gstate = gstate
        self.config(height=RulerCanvas.HEIGHT)
        self._update_scrollregion()

    def _bind_event_handlers(self):
        self.bind('<Configure>', self._on_window_resize)

    def _on_window_resize(self, event):
        self._update_scrollregion()

    def _draw(self):
        self._draw_lines()
        self._draw_text()

    def _draw_lines(self):
        canvas_height = int(self.config('height')[4])
        grid_width = self._gstate.width()
        bar_width = self._gstate.bar_width()

        normal_cell_width = self._gstate.cell_width()
        bu_cell_width = self._gstate.cell_width(subdiv='bu_subdiv')
        cell_width = max(normal_cell_width, bu_cell_width)

        for bar in range(int(grid_width / bar_width) + 1):
            x_offset = bar_width * bar
            x_left = grid_width - x_offset
            cells_in_bar = int(math.ceil(min(bar_width, x_left) / cell_width))
            for cell in range(max(1, cells_in_bar)):
                x = x_offset + cell * cell_width

                if x % bar_width == 0:
                    color = RulerCanvas.BAR_LINE_COLOR
                else:
                    color = RulerCanvas.NORMAL_LINE_COLOR

                self.add_to_layer(RulerCanvas.LINE_LAYER, self.create_line,
                    (x, 0, x, canvas_height), fill=color)

    def _draw_text(self):
        canvas_height = int(self.config('height')[4])
        grid_width = self._gstate.width()
        bar_width = self._gstate.bar_width()
        padding = 4

        normal_cell_width = self._gstate.cell_width()
        bu_cell_width = self._gstate.cell_width(subdiv='bu_subdiv')
        cell_width = max(normal_cell_width, bu_cell_width)

        for bar in range(int(grid_width / bar_width) + 1):
            x_offset = bar_width * bar
            x_left = grid_width - x_offset
            cells_in_bar = int(math.ceil(min(bar_width, x_left) / cell_width))
            for cell in range(max(1, cells_in_bar)):
                cell_offset = cell * cell_width
                x = x_offset + padding + cell_offset
                bu = cell_offset / bu_cell_width
                text = "{0}.{1}".format(bar + 1, int(bu + 1))

                self.add_to_layer(RulerCanvas.TEXT_LAYER, self.create_text,
                    (x, canvas_height), text=text, anchor=SW)

    def _update_scrollregion(self):
        sr_height = int(self.config()['height'][4])
        sr_width = self._gstate.width()
        self._scrollregion = (0, 0, sr_width, sr_height)
        self.config(scrollregion=self._scrollregion)

    def _on_subdiv_change(self):
        self.delete(ALL)
        self._draw()

    def _on_zoomx_change(self):
        self._update_scrollregion()
        self.delete(ALL)
        self._draw()

    def _on_length_change(self):
        self._update_scrollregion()
        self.delete(ALL)
        self._draw()

    def _on_timesig_change(self):
        self._update_scrollregion()
        self.delete(ALL)
        self._draw()

    def on_update(self, new_gstate):
        diff = new_gstate.diff(self._gstate)
        self._gstate = new_gstate

        if 'subdiv' in diff:
            self._on_subdiv_change()
        if 'zoomx' in diff:
            self._on_zoomx_change()
        if 'length' in diff:
            self._on_length_change()
        if any(x in diff for x in ['beat_count', 'beat_unit']):
            self._on_timesig_change()