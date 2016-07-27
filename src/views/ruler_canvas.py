import math
from Tkinter import *
from tkFont import Font
from include.custom_canvas import CustomCanvas
from src.rect import Rect
from src.helper import tick_to_px


class RulerCanvas(CustomCanvas):

    CANVAS_HEIGHT = 45
    MARKER_PLAY_WIDTH = 6
    MARKER_PLAY_HEIGHT = 12
    MARKER_TEXT_OFFSET = 4

    COLOR_CANVAS_OUTLINE_NORMAL = "#000000"
    COLOR_CANVAS_OUTLINE_HIGHLIGHT = "#3399FF"
    COLOR_LINE_NORMAL = '#CCCCCC'
    COLOR_LINE_BAR = '#000000'
    COLOR_LINE_END = '#FF0000'
    COLOR_LINE_PLAY = '#00BFFF'
    COLOR_MARKER_END = '#FFCCCC'
    COLOR_MARKER_PLAY = '#80DFFF'

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
        self._play_pos = 0

    def _bind_event_handlers(self):
        self.bind('<Configure>', self._on_window_resize)

    def _draw_grid_lines(self):
        canvas_height = self.winfo_reqheight()
        bar_width = self._gstate.bar_width()
        beat_count, beat_unit = self._gstate.timesig
        bu_subdiv = math.log(float(beat_unit), 2)
        text_width = self._font.measure(
            "{0}.{1}".format(self._gstate.end[0], beat_count))
        min_subdiv = self._gstate.min_subdiv(
            text_width + RulerCanvas.MARKER_TEXT_OFFSET)

        vr_left, vr_top, vr_width, vr_height = self._visibleregion

        for x in self._gstate.xcoords(
            start=vr_left, end=vr_left + vr_width,
            subdiv=min(bu_subdiv, min_subdiv)):
            if x % bar_width:
                color = RulerCanvas.COLOR_LINE_NORMAL
            else:
                color = RulerCanvas.COLOR_LINE_BAR

            coords = (x, 0, x, canvas_height)
            self.add_to_layer(
                3, self.create_line, coords,
                fill=color, tags='line')

    def _draw_line_end(self):
        grid_width = self._gstate.width()
        coords = (grid_width, 0, grid_width,
            RulerCanvas.CANVAS_HEIGHT)

        self.add_to_layer(
            1, self.create_line, coords,
            fill=RulerCanvas.COLOR_LINE_END)

    def _draw_line_play(self):
        zoomx = self._gstate.zoomx
        x = tick_to_px(self._play_pos) * zoomx
        y1 = 0
        y2 = (RulerCanvas.CANVAS_HEIGHT -
            RulerCanvas.MARKER_PLAY_HEIGHT - 1)
        coords = (x, y1, x, y2)

        self.add_to_layer(
            0, self.create_line, coords,
            fill=RulerCanvas.COLOR_LINE_PLAY,
            tags=('line', 'vertical', 'play'))

    def _draw_grid_text(self):
        canvas_height = int(self.config('height')[4])
        bar_width = self._gstate.bar_width()
        bar = self._gstate.end[0]
        beat_count, beat_unit = self._gstate.timesig
        bu_subdiv = math.log(float(beat_unit), 2)
        bu_cell_width = self._gstate.cell_width(
            subdiv=bu_subdiv)
        text_width = self._font.measure(
            "{0}.{1}".format(bar, beat_count))
        min_subdiv = self._gstate.min_subdiv(
            text_width + RulerCanvas.MARKER_TEXT_OFFSET)
        min_cell_width = self._gstate.cell_width(min_subdiv)
        cell_width = max(bu_cell_width, min_cell_width)

        if cell_width < text_width + RulerCanvas.MARKER_TEXT_OFFSET:
            return

        vr_left, vr_top, vr_width, vr_height = self._visibleregion

        for x in self._gstate.xcoords(
            start=vr_left, end=vr_left + vr_width,
            subdiv=min(bu_subdiv, min_subdiv)):
            bar = int(x / bar_width)
            u = int(x / bu_cell_width) % beat_count
            text = '{0}.{1}'.format(bar + 1, int(u + 1))
            coords = (x + RulerCanvas.MARKER_TEXT_OFFSET,
                canvas_height)
            self.add_to_layer(
                3, self.create_text, coords, text=text,
                anchor=SW, font=self._font)

    def _draw_play_marker(self):
        zoomx = self._gstate.zoomx
        x1 = tick_to_px(self._play_pos) * zoomx
        y1 = RulerCanvas.CANVAS_HEIGHT - 1
        x2 = x1 + RulerCanvas.MARKER_PLAY_WIDTH
        y2 = (RulerCanvas.CANVAS_HEIGHT -
            RulerCanvas.MARKER_PLAY_HEIGHT - 1)
        x3 = x1 - RulerCanvas.MARKER_PLAY_WIDTH
        y3 = (RulerCanvas.CANVAS_HEIGHT -
            RulerCanvas.MARKER_PLAY_HEIGHT - 1)

        coords = (x1, y1, x2, y2, x3, y3)
        self.add_to_layer(
            0, self.create_polygon, coords,
            fill=RulerCanvas.COLOR_MARKER_PLAY,
            outline=RulerCanvas.COLOR_LINE_PLAY,
            tags=('marker', 'play'))

    def _draw_end_marker(self):
        grid_width = self._gstate.width()

        marker_rect = Rect(
            right=grid_width, top=0, width=12, height=16)
        x1 = marker_rect.left
        y1 = marker_rect.top
        x2 = marker_rect.right
        y2 = marker_rect.bottom
        coords = (x1, y1, x2, y2)
        self.add_to_layer(
            3, self.create_rectangle, coords,
            fill=RulerCanvas.COLOR_MARKER_END,
            outline=RulerCanvas.COLOR_LINE_END,
            tags='marker')

        coords = (x1 + 3, y1 + 1)
        self.add_to_layer(
            2, self.create_text, coords,
            text='E', anchor=NW,
            tags=('marker', 'end'))

    def _update(self):
        self._update_scrollregion()
        self._update_visibleregion()
        self.delete(ALL)
        self._draw_grid_lines()
        self._draw_line_end()
        self._draw_line_play()
        self._draw_grid_text()
        self._draw_end_marker()
        self._draw_play_marker()

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
        sr_width = max(grid_width, self.winfo_width())
        sr_height = max(grid_height, self.winfo_height())
        scrollregion = (0, 0, sr_width, sr_height)
        self.config(scrollregion=scrollregion)

    def _on_window_resize(self, event=None):
        self._update()

    def on_update(self, new_gstate):
        diff = self._gstate - new_gstate
        self._gstate = new_gstate

        if diff: self._update()

    def xview(self, *args):
        CustomCanvas.xview(self, *args)
        self._update()

    def set_play_pos(self, ticks):
        self._play_pos = ticks
        self.delete(*self.find_withtags('line', 'play'))
        self.delete(*self.find_withtags('marker', 'play'))
        self._draw_line_play()
        self._draw_play_marker()