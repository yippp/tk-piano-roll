import math
from Tkinter import *
from tkFont import Font
from include.custom_canvas import CustomCanvas
from src.rect import Rect


class RulerCanvas(CustomCanvas):

    CANVAS_HEIGHT = 40
    TEXT_OFFSET = 4

    LAYER_LINE_END = 0
    LAYER_MARKER_TEXT = 1
    LAYER_MARKER_RECT = 2
    LAYER_LINE_NORMAL = 3
    LAYER_TEXT = 3

    COLOR_CANVAS_OUTLINE_NORMAL = "#000000"
    COLOR_CANVAS_OUTLINE_HIGHLIGHT = "#3399FF"
    COLOR_LINE_NORMAL = '#CCCCCC'
    COLOR_LINE_BAR = '#000000'
    COLOR_LINE_END = '#FF0000'
    COLOR_MARKER_RECT = '#FFCCCC'

    def __init__(self, parent, gstate, **kwargs):
        CustomCanvas.__init__(self, parent, **kwargs)

        self._init_data(gstate)
        self._init_ui()
        self._bind_event_handlers()

    def _init_ui(self):
        self.config(height=RulerCanvas.CANVAS_HEIGHT, bg='white')

    def _init_data(self, gstate):
        self._gstate = gstate
        self._font = Font(family='sans-serif', size=9)

    def _bind_event_handlers(self):
        self.bind('<Configure>', self._on_window_resize)

    def _draw_lines(self):
        canvas_height = int(self.config('height')[4])
        grid_width = self._gstate.width()
        bar_width = self._gstate.bar_width()
        bar = self._gstate.end[0]
        beat_count = self._gstate.beat_count
        bu_cell_width = self._gstate.cell_width(
            subdiv='bu_subdiv')
        text_width = self._font.measure(
            "{0}.{1}".format(bar, beat_count))
        min_cell_width = self._gstate.min_cell_width(
            text_width + RulerCanvas.TEXT_OFFSET)
        cell_width = max(bu_cell_width, min_cell_width)

        vr_left, vr_top, vr_width, vr_height = self._visibleregion

        bar_start = int(vr_left / bar_width)
        bars = int(math.ceil(
            min(vr_width, grid_width) / float(bar_width))) + 1

        for bar in range(bar_start, bar_start + bars):
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
                    RulerCanvas.LAYER_LINE_NORMAL, self.create_line,
                    (x, 0, x, canvas_height), fill=color)


        self.add_to_layer(
            RulerCanvas.LAYER_LINE_END, self.create_line,
            (grid_width, 0, grid_width, RulerCanvas.CANVAS_HEIGHT),
            fill=RulerCanvas.COLOR_LINE_END)

    def _draw_text(self):
        canvas_height = int(self.config('height')[4])
        grid_width = self._gstate.width()
        bar_width = self._gstate.bar_width()
        bar = self._gstate.end[0]
        beat_count = self._gstate.beat_count

        bu_cell_width = self._gstate.cell_width(subdiv='bu_subdiv')
        text_width = self._font.measure("{0}.{1}".format(bar, beat_count))
        min_cell_width = self._gstate.min_cell_width(
            text_width + RulerCanvas.TEXT_OFFSET)
        cell_width = max(bu_cell_width, min_cell_width)

        if cell_width < text_width + RulerCanvas.TEXT_OFFSET:
            return

        vr_left, vr_top, vr_width, vr_height = self._visibleregion

        bar_start = int(vr_left / bar_width)
        bars = int(math.ceil(
            min(vr_width, grid_width) / float(bar_width))) + 1

        for bar in range(bar_start, bar_start + bars):
            x_offset = bar_width * bar
            x_left = grid_width - x_offset
            cells_in_bar = int(math.ceil(min(bar_width, x_left) / cell_width))
            for cell in range(max(1, cells_in_bar)):
                cell_offset = cell * cell_width
                x = x_offset + RulerCanvas.TEXT_OFFSET + cell_offset
                u = cell_offset / bu_cell_width
                text = "{0}.{1}".format(bar + 1, int(u + 1))

                self.add_to_layer(RulerCanvas.LAYER_TEXT, self.create_text,
                    (x, canvas_height), text=text, anchor=SW, font=self._font)

    def _draw_end_marker(self):
        grid_width = self._gstate.width()

        marker_rect = Rect(
            right=grid_width, top=0, width=12, height=16)
        x1 = marker_rect.left
        y1 = marker_rect.top
        x2 = marker_rect.right
        y2 = marker_rect.bottom
        self.add_to_layer(
            RulerCanvas.LAYER_MARKER_RECT, self.create_rectangle,
            (x1, y1, x2, y2), fill=RulerCanvas.COLOR_MARKER_RECT,
            outline=RulerCanvas.COLOR_LINE_END, tags='marker')

        self.add_to_layer(
            RulerCanvas.LAYER_MARKER_TEXT, self.create_text,
                (x1 + 3, y1 + 1), text='E', anchor=NW, tags='marker')

    def _update(self):
        self._update_visibleregion()
        self._update_scrollregion()
        self.delete(ALL)
        self._draw_lines()
        self._draw_text()
        self._draw_end_marker()

    def _update_visibleregion(self):
        vr_left = self.canvasx(0)
        vr_top = self.canvasy(0)
        vr_width = self.winfo_width()
        vr_height = self.winfo_height()
        self._visibleregion = (vr_left, vr_top,
            vr_width, vr_height)

    def _update_scrollregion(self):
        grid_width = self._gstate.width()
        grid_height = self._gstate.height()
        vr_width = self._visibleregion[2]
        vr_height = self._visibleregion[3]

        sr_width = max(grid_width, vr_width)
        sr_height = max(grid_height, vr_height)
        self._scrollregion = (0, 0, sr_width, sr_height)
        self.config(scrollregion=self._scrollregion)

    def _on_window_resize(self, event=None):
        self._update()

    def on_update(self, new_gstate):
        diff = self._gstate - new_gstate
        self._gstate = new_gstate

        if diff: self._update()

    def xview(self, *args):
        CustomCanvas.xview(self, *args)
        self._update()