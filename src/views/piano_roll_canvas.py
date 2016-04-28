import math
from Tkinter import *
from ..const import SNAP_DICT, DEFAULT_BAR_WIDTH_IN_PX
from include.custom_canvas import CustomCanvas
from include.rect import Rect

__all__ = ['PianoRollCanvas']

class PianoRollCanvas(CustomCanvas):

    DEFAULT_CELL_HEIGHT_IN_PX = 10
    GRID_HEIGHT_IN_CELLS = 128
    MIN_CELL_WIDTH = 20

    SELECT = 0
    PEN = 1
    ERASER = 2

    NORMAL_LINE_COLOR = "#CCCCCC"
    BAR_LINE_COLOR = "#000000"
    NORMAL_OUTLINE_COLOR = "#000000"
    SELECT_OUTLINE_COLOR = "#FF0000"
    NORMAL_FILL_COLOR = "#FF0000"
    SELECT_FILL_COLOR = "#990000"

    def __init__(self, parent, **kwargs):
        CustomCanvas.__init__(self, parent, width=640, height=480, bg='white', **kwargs)
        self.parent = parent

        self._init_data()
        self._bind_event_handlers()
        self._draw_lines()

    def _init_data(self):
        self._grid_data = {
            'subdiv': SNAP_DICT.values()[0],
            'zoomx': 1,
            'zoomy': 1,
            'length': DEFAULT_BAR_WIDTH_IN_PX
        }

        self._drag_data = {
            'x': 0,
            'y': 0
        }

        self._selection = []

        self._rects = {}

        self._tool = 0

        scrollregion_height = (PianoRollCanvas.GRID_HEIGHT_IN_CELLS *
            PianoRollCanvas.DEFAULT_CELL_HEIGHT_IN_PX)
        self._scrollregion = [0, 0, 640, scrollregion_height]
        self._visibleregion = [0, 0, 640, 480]
        self.config(scrollregion=self._scrollregion)

    def _bind_event_handlers(self):
        self.bind('<ButtonPress-1>', self._on_bttnone_press)
        self.bind('<Control-1>', self._on_bttnone_ctrl)
        self.bind('<Configure>', self._update_visibleregion)
        self.bind('<Delete>', self._on_delete)

    def _on_bttnone_press(self, event):
        self._deselect_rect()

        if self._tool == PianoRollCanvas.SELECT:
            self._select_rect(event)
        if self._tool == PianoRollCanvas.PEN:
            self._add_rect(event)
        if self._tool == PianoRollCanvas.ERASER:
            self._delete_rect(event)

        self._drag_data['x'] = event.x
        self._drag_data['y'] = event.y

        self.focus_set()

    def _on_bttnone_ctrl(self, event):
        if self._tool == PianoRollCanvas.SELECT:
            self._select_rect(event)

    def _on_bttnone_release(self, event):
        pass

    def _on_bttnone_motion(self, event):
        pass

    def _on_delete(self, event):
        for id in self._selection:
            del self._rects[id]
            self.delete(id)

        self._selection = []

    def _draw(self):
        self._draw_rects()
        self._draw_lines()

    def _draw_rects(self):
        zoomx = self._grid_data['zoomx']
        zoomy = self._grid_data['zoomy']

        for id, rect in self._rects.items():
            x1 = rect.left * zoomx
            y1 = rect.top * zoomy
            x2 = x1 + rect.width * zoomx
            y2 = y1 + rect.height * zoomy
            coords = (x1, y1, x2, y2)

            if (id in self._selection):
                new_id = self.add_to_layer(0, self.create_rectangle, coords,
                    outline=PianoRollCanvas.SELECT_OUTLINE_COLOR,
                    fill=PianoRollCanvas.SELECT_FILL_COLOR,
                    tags='rect')
                self._selection.append(new_id)
            else:
                new_id = self.add_to_layer(0, self.create_rectangle, coords,
                    outline=PianoRollCanvas.NORMAL_OUTLINE_COLOR,
                    fill=PianoRollCanvas.NORMAL_FILL_COLOR, tags='rect')

            self._rects[new_id] = self._rects.pop(id)

    def _draw_lines(self):
        self._draw_horizontal_lines()
        self._draw_vertical_lines()

    def _draw_horizontal_lines(self):
        zoomx = self._grid_data['zoomx']
        zoomy = self._grid_data['zoomy']
        length = self._grid_data['length']

        cell_height = self._calc_cell_height(zoomy)
        n = int(self._visibleregion[3] / cell_height) + 1

        x1 = self.canvasx(0)
        x2 = min(self.canvasx(self._visibleregion[2]), length * zoomx)

        yorigin = self.canvasy(0)
        offset = cell_height * math.ceil(yorigin / cell_height)

        for j in range(n):
            y = j * cell_height + offset
            color = PianoRollCanvas.NORMAL_LINE_COLOR
            self.add_to_layer(2, self.create_line, (x1, y, x2, y),
                fill=color, tags=('line', 'horizontal'))

    def _draw_vertical_lines(self):
        subdiv = self._grid_data['subdiv']
        zoomx = self._grid_data['zoomx']
        length = self._grid_data['length']
        visibleregion_width = self._visibleregion[2]
        visibleregion_height = self._visibleregion[3]

        cell_width = self._calc_cell_width(subdiv, zoomx)
        n = int(min(length * zoomx, visibleregion_width) / cell_width) + 1

        y1 = self.canvasy(0)
        y2 = self.canvasy(visibleregion_height)
        xorigin = self.canvasx(0)

        if length >= visibleregion_width:
            offset = cell_width * math.ceil(xorigin / cell_width)
        else:
            offset = 0

        for i in range(n):
            x = i * cell_width + offset
            color = self._get_line_color(x)
            self.add_to_layer(1, self.create_line, (x, y1, x, y2),
                fill=color, tags=('line', 'vertical'))

    def _get_line_color(self, xcoord):
        zoomx = self._grid_data['zoomx']

        return (PianoRollCanvas.BAR_LINE_COLOR if xcoord %
            (DEFAULT_BAR_WIDTH_IN_PX * zoomx) == 0 else
            PianoRollCanvas.NORMAL_LINE_COLOR)

    def _calc_cell_width(self, subdiv, zoomx=1):
        for i in range(subdiv + 1):
            cell_width = DEFAULT_BAR_WIDTH_IN_PX * zoomx / 2**(subdiv - i)
            if (cell_width >= PianoRollCanvas.MIN_CELL_WIDTH):
                return cell_width

    def _calc_cell_height(self, zoomy=1):
        return PianoRollCanvas.DEFAULT_CELL_HEIGHT_IN_PX * zoomy

    def _update_scrollregion(self):
        zoomx = self._grid_data['zoomx']
        zoomy = self._grid_data['zoomy']
        length = self._grid_data['length']
        visibleregion_width = self._visibleregion[2]

        scrollregion_width = max(length * zoomx, visibleregion_width)
        scrollregion_height = (PianoRollCanvas.GRID_HEIGHT_IN_CELLS *
            PianoRollCanvas.DEFAULT_CELL_HEIGHT_IN_PX * zoomy)
        self.config(scrollregion=(0, 0, scrollregion_width, scrollregion_height))

    def _update_visibleregion(self, event):
        self._visibleregion[2] = self.winfo_width() - 2
        self._visibleregion[3] = self.winfo_height() - 2

        self.delete(*self.find_withtags('line'))
        self._draw_lines()

    def _add_rect(self, event):
        mousex = event.x
        mousey = event.y
        zoomx = self._grid_data['zoomx']
        zoomy = self._grid_data['zoomy']
        length = self._grid_data['length']
        visibleregion_height = self._visibleregion[3]
        grid_rect = Rect(0, 0, length * zoomx, visibleregion_height)

        if (grid_rect.collide_point(mousex, mousey)):
            subdiv = self._grid_data['subdiv']

            canvasx = self.canvasx(mousex)
            canvasy = self.canvasy(mousey)

            cellw = DEFAULT_BAR_WIDTH_IN_PX / 2**subdiv
            cellh = PianoRollCanvas.DEFAULT_CELL_HEIGHT_IN_PX
            cellwz = cellw * zoomx
            cellhz = cellh * zoomy

            rectx = cellw * int(canvasx / cellwz)
            recty = cellh * int(canvasy / cellhz)
            rectxz = rectx * zoomx
            rectyz = recty * zoomy

            coords = (rectxz, rectyz, rectxz + cellwz, rectyz + cellhz)
            id = self.add_to_layer(0, self.create_rectangle, coords,
                outline=PianoRollCanvas.SELECT_OUTLINE_COLOR,
                fill=PianoRollCanvas.SELECT_FILL_COLOR, tags='rect')
            self._selection.append(id)
            self._rects[id] = Rect(rectx, recty, cellw, cellh)

    def _select_rect(self, event):
        mousex = event.x
        mousey = event.y
        id = self._rect_at(mousex, mousey)

        if id:
            if id in self._selection:
                outline_color = PianoRollCanvas.NORMAL_OUTLINE_COLOR
                fill_color = PianoRollCanvas.NORMAL_FILL_COLOR
                self._selection.remove(id)
            else:
                outline_color = PianoRollCanvas.SELECT_OUTLINE_COLOR
                fill_color = PianoRollCanvas.SELECT_FILL_COLOR
                self._selection.append(id)

            self.itemconfig(id, fill=fill_color, outline=outline_color)

    def _deselect_rect(self):
        for id in self._rects:
            self.itemconfig(id, fill=PianoRollCanvas.NORMAL_FILL_COLOR,
                outline=PianoRollCanvas.NORMAL_OUTLINE_COLOR)
            self._selection = []

    def _delete_rect(self, event):
        mousex = event.x
        mousey = event.y
        id = self._rect_at(mousex, mousey)

        if id:
            del self._rects[id]
            self.delete(id)

    def _rect_at(self, mousex, mousey):
        ids = self.find_withtags('rect')
        for id in ids:
            coords = self.coords(id)
            x = coords[0]
            y = coords[1]
            w = coords[2] - x
            h = coords[3] - y
            x0 = self.canvasx(0)
            y0 = self.canvasy(0)

            r = Rect(x - x0, y - y0, w, h)
            if (r.collide_point(mousex, mousey)):
                return id

        return None

    def set_subdiv(self, value):
        self._grid_data['subdiv'] = value
        self.delete(*self.find_withtags('line', 'vertical'))
        self._draw_lines()
        self._adjust_layers()

    def set_zoomx(self, value):
        self._grid_data['zoomx'] = value

        self._update_scrollregion()
        self.delete(ALL)
        self._draw()
        self._adjust_layers()

    def set_zoomy(self, value):
        self._grid_data['zoomy'] = value

        self._update_scrollregion()
        self.delete(ALL)
        self._draw()
        self._adjust_layers()

    def set_length(self, value):
        self._grid_data['length'] = value

        self._update_scrollregion()
        self.delete(*self.find_withtags('line'))
        self._draw_lines()
        self._adjust_layers()

    def set_tool(self, value):
        self._tool = value

    def xview(self, *args):
        self.delete(*self.find_withtags('line'))
        CustomCanvas.xview(self, *args)
        self._draw_lines()
        self._adjust_layers()

    def yview(self, *args):
        self.delete(*self.find_withtags('line'))
        CustomCanvas.yview(self, *args)
        self._draw_lines()
        self._adjust_layers()