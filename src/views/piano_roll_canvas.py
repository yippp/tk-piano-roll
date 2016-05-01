import math
from Tkinter import *
from ..const import SNAP_DICT, DEFAULT_BAR_WIDTH_IN_PX
from include.custom_canvas import CustomCanvas
from include.rect import Rect

__all__ = ['PianoRollCanvas']

class PianoRollCanvas(CustomCanvas):

    DEFAULT_CELL_HEIGHT_IN_PX = 10
    MIN_CELL_WIDTH_IN_PX = 20
    GRID_HEIGHT_IN_CELLS = 128

    SELECT_TOOL = 0
    PEN_TOOL = 1
    ERASER_TOOL = 2

    NORMAL_LINE_COLOR = "#CCCCCC"
    BAR_LINE_COLOR = "#000000"
    NORMAL_OUTLINE_COLOR = "#000000"
    SELECT_OUTLINE_COLOR = "#FF0000"
    NORMAL_FILL_COLOR = "#FF0000"
    SELECT_FILL_COLOR = "#990000"
    CTRL_MASK = 0x0004

    def __init__(self, parent, **kwargs):
        CustomCanvas.__init__(self, parent, width=640, height=480, bg='white', **kwargs)
        self.parent = parent

        self._init_data()
        self._bind_event_handlers()
        self._draw_lines()

    def _init_data(self):
        self._rects = {}
        self._tool = 0
        self._grid_data = {
            'subdiv': SNAP_DICT.values()[0],
            'zoomx': 1,
            'zoomy': 1,
            'length': DEFAULT_BAR_WIDTH_IN_PX
        }
        self._drag_data = {
            'x': 0,
            'y': 0,
            'dx': 0,
            'dy': 0,
            'anchors': {}
        }
        self._selected = []
        self._clicked_on_selected_rect = False

        scrollregion_height = (PianoRollCanvas.GRID_HEIGHT_IN_CELLS *
            PianoRollCanvas.DEFAULT_CELL_HEIGHT_IN_PX)
        self._scrollregion = [0, 0, 640, scrollregion_height]
        self._visibleregion = [0, 0, 640, 480]
        self.config(scrollregion=self._scrollregion)

    def _bind_event_handlers(self):
        self.bind('<ButtonPress-1>', self._on_bttnone_press)
        self.bind('<ButtonRelease-1>', self._on_bttnone_release)
        self.bind('<B1-Motion>', self._on_bttnone_motion)
        self.bind('<Control-1>', self._on_bttnone_ctrl)
        self.bind('<Configure>', self._update_visibleregion)
        self.bind('<Delete>', self._on_delete)

    def _on_bttnone_press(self, event):
        if self._tool == PianoRollCanvas.SELECT_TOOL:
            self._select(event)
        if self._tool == PianoRollCanvas.PEN_TOOL:
            self._deselect_rects(*self._selected)
            self._add_rect(event)
        if self._tool == PianoRollCanvas.ERASER_TOOL:
            self._deselect_rects(*self._selected)
            self._delete(event)

        self._drag_data['x'] = event.x
        self._drag_data['y'] = event.y
        self._drag_data['dx'] = 0
        self._drag_data['dy'] = 0
        self._update_drag_anchors()

        self.focus_set()

    def _on_bttnone_ctrl(self, event):
        if self._tool == PianoRollCanvas.SELECT_TOOL:
            id = self._rect_at(event.x, event.y)
            # clicked on selected rect
            if id != None and id in self._selected:
                self._deselect_rects(id)
            # clicked on unselected rect
            elif id != None and id not in self._selected:
                self._select_rects(id)

        self._update_drag_anchors()
        self._clicked_on_selected_rect = False

    def _on_bttnone_release(self, event):
        dragged = self._drag_data['dx'] != 0 or self._drag_data['dy'] != 0
        if len(self._selected) > 1 and self._clicked_on_selected_rect and not dragged:
            self._deselect_rects(*self._selected)
            self._select_rects(self._rect_at(event.x, event.y))

    def _on_bttnone_motion(self, event):
        ctrl_pressed = event.state & PianoRollCanvas.CTRL_MASK == PianoRollCanvas.CTRL_MASK

        if (self._tool == PianoRollCanvas.SELECT_TOOL and not ctrl_pressed):
            subdiv = self._grid_data['subdiv']
            zoomx = self._grid_data['zoomx']
            zoomy = self._grid_data['zoomy']

            drag_x = self._drag_data['x']
            drag_y = self._drag_data['y']

            cell_width = self._calc_cell_width(subdiv)
            cell_height = self._calc_cell_height()
            cell_width_z = cell_width * zoomx
            cell_height_z = cell_height * zoomy

            dx = cell_width * round(float(event.x - drag_x) / cell_width_z)
            dy = cell_height * round(float(event.y - drag_y) / cell_height_z)

            for id, coords in self._drag_data['anchors'].items():
                self._rects[id].left = coords.left
                self._rects[id].top = coords.top
                self._rects[id].move_ip(dx, dy)

            self._drag_data['dx'] = dx
            self._drag_data['dy'] = dy

            self.delete(*self.find_withtags('rect'))
            self._draw_rects()

    def _on_delete(self, event):
        self._delete_rects(*self._selected)
        self._selected = []

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

            if (id in self._selected):
                new_id = self.add_to_layer(0, self.create_rectangle, coords,
                    outline=PianoRollCanvas.SELECT_OUTLINE_COLOR,
                    fill=PianoRollCanvas.SELECT_FILL_COLOR,
                    tags='rect')
                self._selected.remove(id)
                self._selected.append(new_id)
            else:
                new_id = self.add_to_layer(0, self.create_rectangle, coords,
                    outline=PianoRollCanvas.NORMAL_OUTLINE_COLOR,
                    fill=PianoRollCanvas.NORMAL_FILL_COLOR, tags='rect')

            self._rects[new_id] = self._rects.pop(id)
            if id in self._drag_data['anchors']:
                self._drag_data['anchors'][new_id] = self._drag_data['anchors'].pop(id)

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

        max_subdiv = self._calc_max_subdiv()
        cell_width = self._calc_cell_width(min(subdiv, max_subdiv), zoomx)

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
            if x % (DEFAULT_BAR_WIDTH_IN_PX * zoomx) == 0:
                color = PianoRollCanvas.BAR_LINE_COLOR
            else:
                color = PianoRollCanvas.NORMAL_LINE_COLOR

            self.add_to_layer(1, self.create_line, (x, y1, x, y2),
                fill=color, tags=('line', 'vertical'))

    def _calc_max_subdiv(self):
        zoomx = self._grid_data['zoomx']
        n_snap_opts = len(SNAP_DICT)

        for i in range(n_snap_opts - 1):
            cell_width = self._calc_cell_width(n_snap_opts - i, zoomx)
            if (cell_width >= PianoRollCanvas.MIN_CELL_WIDTH_IN_PX):
                return i

    def _calc_cell_width(self, subdiv, zoomx=1.0):
        return DEFAULT_BAR_WIDTH_IN_PX * zoomx / 2**subdiv

    def _calc_cell_height(self, zoomy=1.0):
        return PianoRollCanvas.DEFAULT_CELL_HEIGHT_IN_PX * zoomy

    def _update_scrollregion(self):
        zoomx = self._grid_data['zoomx']
        zoomy = self._grid_data['zoomy']
        length = self._grid_data['length']
        visibleregion_width = self._visibleregion[2]

        cell_height = self._calc_cell_height(zoomy)

        scrollregion_width = max(length * zoomx, visibleregion_width)
        scrollregion_height = (PianoRollCanvas.GRID_HEIGHT_IN_CELLS * cell_height)
        self.config(scrollregion=(0, 0, scrollregion_width, scrollregion_height))

    def _update_visibleregion(self, event):
        self._visibleregion[2] = self.winfo_width() - 2
        self._visibleregion[3] = self.winfo_height() - 2

        self.delete(*self.find_withtags('line'))
        self._draw_lines()

    def _update_drag_anchors(self):
        self._drag_data['anchors'].clear()
        for id in self._selected:
            self._drag_data['anchors'][id] = self._rects[id].copy()

    def _add_rect(self, event):
        zoomx = self._grid_data['zoomx']
        length = self._grid_data['length']
        visibleregion_height = self._visibleregion[3]
        grid_rect = Rect(0, 0, length * zoomx, visibleregion_height)

        canvasx = self.canvasx(event.x)
        canvasy = self.canvasy(event.y)

        if (grid_rect.collide_point(canvasx, canvasy)):
            zoomy = self._grid_data['zoomy']
            subdiv = self._grid_data['subdiv']

            cell_width = self._calc_cell_width(subdiv)
            cell_height = self._calc_cell_height()
            cell_width_z = cell_width * zoomx
            cell_height_z = cell_height * zoomy

            rect_x = cell_width * int(canvasx / cell_width_z)
            rect_y = cell_height * int(canvasy / cell_height_z)
            rect_x_z = rect_x * zoomx
            rect_y_z = rect_y * zoomy

            coords = (rect_x_z, rect_y_z, rect_x_z + cell_width_z, rect_y_z + cell_height_z)
            id = self.add_to_layer(0, self.create_rectangle, coords,
                outline=PianoRollCanvas.SELECT_OUTLINE_COLOR,
                fill=PianoRollCanvas.SELECT_FILL_COLOR, tags='rect')
            self._selected.append(id)
            self._rects[id] = Rect(rect_x, rect_y, cell_width, cell_height)

    def _select(self, event):
        id = self._rect_at(event.x, event.y)
        # clicked on empty area of the grid
        if not id:
            self._deselect_rects(*self._selected)
            self._clicked_on_selected_rect = False
        elif id in self._selected:
            self._clicked_on_selected_rect = True
        # clicked on unselected rect
        else:
            self._deselect_rects(*self._selected)
            self._select_rects(id)
            self._clicked_on_selected_rect = False

    def _select_rects(self, *ids):
        for id in ids:
            self.itemconfig(id, fill=PianoRollCanvas.SELECT_FILL_COLOR,
                outline=PianoRollCanvas.SELECT_FILL_COLOR)
            self._selected.append(id)

    def _deselect_rects(self, *ids):
        for id in ids:
            self.itemconfig(id, fill=PianoRollCanvas.NORMAL_FILL_COLOR,
                outline=PianoRollCanvas.NORMAL_OUTLINE_COLOR)
            self._selected.remove(id)

    def _delete(self, event):
        id = self._rect_at(event.x, event.y)
        if id != None:
            self._delete_rects(id)

    def _delete_rects(self, *ids):
        for id in ids:
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