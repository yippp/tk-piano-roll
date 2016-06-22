import math
from Tkinter import *
from include.custom_canvas import CustomCanvas


class RulerCanvas(CustomCanvas):

    CANVAS_HEIGHT = 32

    LAYER_LINE = 0
    LAYER_TEXT = 0

    COLOR_LINE_NORMAL = '#CCCCCC'
    COLOR_LINE_BAR = '#808080'
    COLOR_LINE_END = '#0000FF'
    COLOR_CANVAS_OUTLINE_NORMAL = "#000000"
    COLOR_CANVAS_OUTLINE_HIGHLIGHT = "#3399FF"

    def __init__(self, parent, gstate, **kwargs):
        CustomCanvas.__init__(self, parent, **kwargs)

        self._init_data(gstate)
        self._init_ui()
        self._bind_event_handlers()

    def _init_ui(self):
        self.config(height=RulerCanvas.CANVAS_HEIGHT, bg='white')

    def _init_data(self, gstate):
        self._gstate = gstate
        self.config(height=RulerCanvas.CANVAS_HEIGHT)

    def _bind_event_handlers(self):
        self.bind('<Configure>', self._on_window_resize)

    def _on_window_resize(self, event=None):
        self.delete(ALL)
        self._update_visibleregion()
        self._update_scrollregion()
        self._draw()

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

        bar_start = int(self._visibleregion[0] / bar_width)
        nbars = int(min(self._visibleregion[2], grid_width) / bar_width) + 1

        for bar in range(bar_start, bar_start + nbars):
            x_offset = bar_width * bar
            bar_left = grid_width - x_offset
            cells_in_bar = int(math.ceil(min(bar_width, bar_left) / cell_width))
            for cell in range(max(1, cells_in_bar)):
                x = x_offset + cell * cell_width

                if x % bar_width == 0:
                    color = RulerCanvas.COLOR_LINE_BAR
                else:
                    color = RulerCanvas.COLOR_LINE_NORMAL

                self.add_to_layer(
                    RulerCanvas.LAYER_LINE, self.create_line,
                    (x, 0, x, canvas_height), fill=color)


        self.add_to_layer(
            RulerCanvas.LAYER_LINE, self.create_line,
            (grid_width, 0, grid_width, RulerCanvas.CANVAS_HEIGHT),
            fill=RulerCanvas.COLOR_LINE_END)

    def _draw_text(self):
        canvas_height = int(self.config('height')[4])
        grid_width = self._gstate.width()
        bar_width = self._gstate.bar_width()
        padding = 4

        normal_cell_width = self._gstate.cell_width()
        bu_cell_width = self._gstate.cell_width(subdiv='bu_subdiv')
        cell_width = max(normal_cell_width, bu_cell_width)

        bar_start = int(self._visibleregion[0] / bar_width)
        nbars = int(min(self._visibleregion[2], grid_width) / bar_width) + 1

        for bar in range(bar_start, bar_start + nbars):
            x_offset = bar_width * bar
            x_left = grid_width - x_offset
            cells_in_bar = int(math.ceil(min(bar_width, x_left) / cell_width))
            for cell in range(max(1, cells_in_bar)):
                cell_offset = cell * cell_width
                x = x_offset + padding + cell_offset
                u = cell_offset / bu_cell_width
                text = "{0}.{1}".format(bar + 1, int(u + 1))

                self.add_to_layer(RulerCanvas.LAYER_TEXT, self.create_text,
                    (x, canvas_height), text=text, anchor=SW)

    def _update_visibleregion(self):
        vr_left = self.canvasx(0)
        vr_top = self.canvasx(0)
        vr_width = self.winfo_width()
        vr_height = self.winfo_height()
        self._visibleregion = vr_left, vr_top, vr_width, vr_height

    def _update_scrollregion(self):
        sr_width = self._gstate.width()
        sr_height = self.winfo_height()
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
        self._update_visibleregion()
        self.delete(ALL)
        self._draw()

    def _on_timesig_change(self):
        self._update_scrollregion()
        self.delete(ALL)
        self._draw()

    def on_update(self, new_gstate):
        diff = self._gstate - new_gstate
        self._gstate = new_gstate

        if 'subdiv' in diff:
            self._on_subdiv_change()
        if 'zoomx' in diff:
            self._on_zoomx_change()
        if 'length' in diff:
            self._on_length_change()
        if any(x in diff for x in ['beat_count', 'beat_unit']):
            self._on_timesig_change()

    def xview(self, *args):
        self.delete(ALL)
        CustomCanvas.xview(self, *args)
        self._update_visibleregion()
        self._draw()