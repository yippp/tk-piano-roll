import math
from sets import Set
from Tkinter import *
from ..const import SNAP_DICT, DEFAULT_BAR_WIDTH_IN_PX
from include.custom_canvas import CustomCanvas
from include.rect import Rect

__all__ = ['PianoRollCanvas']


class PianoRollCanvas(CustomCanvas):

    DEFAULT_CELL_HEIGHT_IN_PX = 10
    MIN_CELL_WIDTH_IN_PX = 20
    GRID_HEIGHT_IN_CELLS = 128

    SEL_TOOL = 0
    PEN_TOOL = 1
    ERASER_TOOL = 2

    SEL_REGION_LAYER = 0
    RECT_LAYER = 1
    VL_LAYER = 2
    HL_LAYER = 3

    NORMAL_LINE_COLOR = "#CCCCCC"
    BAR_LINE_COLOR = "#000000"
    NORMAL_OUTLINE_COLOR = "#000000"
    SEL_OUTLINE_COLOR = "#FF0000"
    NORMAL_FILL_COLOR = "#FF0000"
    SEL_FILL_COLOR = "#990000"

    CTRL_MASK = 0x0004

    SELECTED = -1
    ALL = -2

    CLICKED_ON_EMPTY_AREA = 0
    CLICKED_ON_UNSELECTED_RECT = 1
    CLICKED_ON_SELECTED_RECT = 2
    CLICKED_CTRL_ON_SELECTED_RECT = 3

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
            'mousex': 0,
            'mousey': 0,
            'dx': 0,
            'dy': 0,
            'left': 0,
            'top': 0,
            'right': 0,
            'bottom': 0,
            'anchors': {}
        }
        self._selected = Set()
        self._click_type = PianoRollCanvas.CLICKED_ON_EMPTY_AREA

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
        self.bind('<Configure>', self._update_regions)

    def _on_bttnone_press(self, event):
        if self._tool == PianoRollCanvas.SEL_TOOL:
            self._select(event)
        if self._tool == PianoRollCanvas.PEN_TOOL:
            self.deselect_rects(*self._selected)
            self._add_rect(event)
        if self._tool == PianoRollCanvas.ERASER_TOOL:
            self.deselect_rects(*self._selected)
            self._remove(event)

        self._drag_data['mousex'] = event.x
        self._drag_data['mousey'] = event.y
        self._drag_data['dx'] = 0
        self._drag_data['dy'] = 0
        self._update_drag_data()

        self.parent.focus_set()

    def _on_bttnone_ctrl(self, event):
        if self._tool == PianoRollCanvas.SEL_TOOL:
            id = self._rect_at(event.x, event.y)
            if id == None:
                self._click_type = PianoRollCanvas.CLICKED_ON_EMPTY_AREA
            elif id not in self._selected:
                self.select_rects(id)
                self._update_drag_data()
                self._click_type = PianoRollCanvas.CLICKED_ON_UNSELECTED_RECT
            else:
                self.deselect_rects(id)
                self._update_drag_data()
                self._click_type = PianoRollCanvas.CLICKED_CTRL_ON_SELECTED_RECT

            self._drag_data['mousex'] = event.x
            self._drag_data['mousey'] = event.y

    def _on_bttnone_release(self, event):
        dragged = (self._drag_data['mousex'] - event.x != 0 or
            self._drag_data['mousey'] - event.y != 0)

        if (len(self._selected) > 1 and self._click_type ==
            PianoRollCanvas.CLICKED_ON_SELECTED_RECT and not dragged):
            self.deselect_rects(*self._selected)
            self.select_rects(self._rect_at(event.x, event.y))
        elif (self._tool == PianoRollCanvas.SEL_TOOL == 0 and self._click_type ==
            PianoRollCanvas.CLICKED_ON_EMPTY_AREA and dragged):
            sel_region_id = self.find_withtags('selection_region')[0]
            coords = self.coords(sel_region_id)

            overlapping = self.find_overlapping(*coords)
            rects = self.find_withtags('rect')
            overlapping_rects = set(overlapping).intersection(rects)
            self.select_rects(*overlapping_rects)
            self.delete(sel_region_id)

    def _on_bttnone_motion(self, event):
        if self._tool == PianoRollCanvas.SEL_TOOL:
            if (len(self._selected) > 0 and self._click_type !=
                PianoRollCanvas.CLICKED_ON_EMPTY_AREA):
                self._drag_rects(event.x, event.y)
            elif self._click_type == PianoRollCanvas.CLICKED_ON_EMPTY_AREA:
                self.delete(*self.find_withtags('selection_region'))
                self._draw_selection_region(event.x, event.y)

    def _draw(self):
        self._draw_rects()
        self._draw_lines()

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
            self.add_to_layer(PianoRollCanvas.HL_LAYER,
                self.create_line, (x1, y, x2, y),
                fill=color, tags=('line', 'horizontal'))

    def _draw_vertical_lines(self):
        subdiv = self._grid_data['subdiv']
        zoomx = self._grid_data['zoomx']
        length = self._grid_data['length']
        visibleregion_width = self._visibleregion[2]
        visibleregion_height = self._visibleregion[3]

        max_subdiv = self._calc_max_subdiv(zoomx)
        cell_width = self._calc_cell_width(min(subdiv, max_subdiv), zoomx)

        n = int(min(length * zoomx, visibleregion_width) / cell_width) + 1

        y1 = self.canvasy(0)
        y2 = self.canvasy(visibleregion_height)
        xorigin = self.canvasx(0)

        offset = cell_width * math.ceil(xorigin / cell_width)

        for i in range(n):
            x = i * cell_width + offset
            if x % (DEFAULT_BAR_WIDTH_IN_PX * zoomx) == 0:
                color = PianoRollCanvas.BAR_LINE_COLOR
            else:
                color = PianoRollCanvas.NORMAL_LINE_COLOR

            self.add_to_layer(PianoRollCanvas.VL_LAYER,
                self.create_line, (x, y1, x, y2),
                fill=color, tags=('line', 'vertical'))

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
                new_id = self.add_to_layer(PianoRollCanvas.RECT_LAYER,
                    self.create_rectangle, coords,
                    outline=PianoRollCanvas.SEL_OUTLINE_COLOR,
                    fill=PianoRollCanvas.SEL_FILL_COLOR,
                    tags='rect')
                self.deselect_rects(id)
                self.select_rects(new_id)
            else:
                new_id = self.add_to_layer(PianoRollCanvas.RECT_LAYER,
                    self.create_rectangle, coords,
                    outline=PianoRollCanvas.NORMAL_OUTLINE_COLOR,
                    fill=PianoRollCanvas.NORMAL_FILL_COLOR, tags='rect')

            self._rects[new_id] = self._rects.pop(id)
            if id in self._drag_data['anchors']:
                self._drag_data['anchors'][new_id] = self._drag_data['anchors'].pop(id)

    def _draw_selection_region(self, mousex, mousey):
        x1 = self.canvasx(self._drag_data['mousex'])
        y1 = self.canvasy(self._drag_data['mousey'])
        x2 = self.canvasx(mousex)
        y2 = self.canvasy(mousey)

        coords = (x1, y1, x2, y2)
        self.add_to_layer(PianoRollCanvas.SEL_REGION_LAYER,
            self.create_rectangle, coords, fill='blue', outline='blue',
            stipple='gray25', tags='selection_region')

    def _calc_max_subdiv(self, zoomx):
        n_snap_opts = len(SNAP_DICT)

        for i in range(n_snap_opts - 1, -1, -1):
            cell_width = self._calc_cell_width(i, zoomx)
            if cell_width >= PianoRollCanvas.MIN_CELL_WIDTH_IN_PX:
                return i

    def _calc_cell_width(self, subdiv, zoomx=1.0):
        return DEFAULT_BAR_WIDTH_IN_PX * zoomx / 2**subdiv

    def _calc_cell_height(self, zoomy=1.0):
        return PianoRollCanvas.DEFAULT_CELL_HEIGHT_IN_PX * zoomy

    def _update_regions(self, event):
        self._update_visibleregion()
        self._update_scrollregion()

    def _update_scrollregion(self):
        zoomx = self._grid_data['zoomx']
        zoomy = self._grid_data['zoomy']
        length = self._grid_data['length']
        visibleregion_width = self._visibleregion[2]

        cell_height = self._calc_cell_height(zoomy)

        scrollregion_width = max(length * zoomx, visibleregion_width)
        scrollregion_height = (PianoRollCanvas.GRID_HEIGHT_IN_CELLS * cell_height)
        self.config(scrollregion=(0, 0, scrollregion_width, scrollregion_height))

    def _update_visibleregion(self):
        self._visibleregion[2] = self.winfo_width() - 2
        self._visibleregion[3] = self.winfo_height() - 2

        self.delete(*self.find_withtags('line'))
        self._draw_lines()

    def _update_drag_data(self):
        self._drag_data['anchors'].clear()
        for id in self._selected:
            self._drag_data['anchors'][id] = self._rects[id].copy()

        if len(self._selected) > 0:
            selected_rects = [self._rects[id] for id in self._selected]
            self._drag_data['left'] = sorted(selected_rects, key=lambda r: r.left)[0].left
            self._drag_data['top'] = sorted(selected_rects, key=lambda r: r.top)[0].top
            self._drag_data['right'] = sorted(selected_rects, key=lambda r: r.right, reverse=True)[0].right
            self._drag_data['bottom'] = sorted(selected_rects, key=lambda r: r.bottom, reverse=True)[0].bottom

    def _add_rect(self, event):
        zoomx = self._grid_data['zoomx']
        zoomy = self._grid_data['zoomy']
        length = self._grid_data['length']
        scrollregion_height = self._scrollregion[3]
        grid_rect = Rect(0, 0, length * zoomx, scrollregion_height * zoomy)

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
            id = self.add_to_layer(PianoRollCanvas.RECT_LAYER,
                self.create_rectangle, coords,
                outline=PianoRollCanvas.SEL_OUTLINE_COLOR,
                fill=PianoRollCanvas.SEL_FILL_COLOR, tags='rect')

            self._selected.add(id)
            self._rects[id] = Rect(rect_x, rect_y, cell_width, cell_height)

    def _select(self, event):
        id = self._rect_at(event.x, event.y)
        if id == None:
            self.deselect_rects(*self._selected)
            self._click_type = PianoRollCanvas.CLICKED_ON_EMPTY_AREA
        elif id not in self._selected:
            self.deselect_rects(*self._selected)
            self.select_rects(id)
            self._click_type = PianoRollCanvas.CLICKED_ON_UNSELECTED_RECT
        else:
            self._click_type = PianoRollCanvas.CLICKED_ON_SELECTED_RECT

    def _remove(self, event):
        id = self._rect_at(event.x, event.y)
        if id != None:
            self.remove_rects(id)

    def _drag_rects(self, mousex, mousey):
        subdiv = self._grid_data['subdiv']
        zoomx = self._grid_data['zoomx']
        zoomy = self._grid_data['zoomy']
        length = self._grid_data['length']

        scrollregion_height = self._scrollregion[3]

        drag_x = self._drag_data['mousex']
        drag_y = self._drag_data['mousey']

        cell_width = self._calc_cell_width(subdiv)
        cell_height = self._calc_cell_height()
        cell_width_z = cell_width * zoomx
        cell_height_z = cell_height * zoomy

        dx = cell_width * round(float(mousex - drag_x) / cell_width_z)
        dy = cell_height * round(float(mousey - drag_y) / cell_height_z)

        grid_rect = Rect(0, 0, length, scrollregion_height)

        if self._drag_data['left'] + dx < grid_rect.left:
            dx = grid_rect.left - self._drag_data['left']
        elif self._drag_data['right'] + dx >= grid_rect.right:
            dx = grid_rect.right - self._drag_data['right']

        if self._drag_data['top'] + dy < grid_rect.top:
            dy = grid_rect.top - self._drag_data['top']
        elif self._drag_data['bottom'] + dy >= grid_rect.bottom:
            dy = grid_rect.bottom - self._drag_data['bottom']

        for id, coords in self._drag_data['anchors'].items():
            self._rects[id].left = coords.left
            self._rects[id].top = coords.top
            self._rects[id].move_ip(dx, dy)

        self._drag_data['dx'] = dx
        self._drag_data['dy'] = dy

        self.delete(*self.find_withtags('rect'))
        self._draw_rects()

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

    def select_rects(self, *args):
        argc = len(args)
        if argc == 0:
            return
        if argc == 1 and args[0] == PianoRollCanvas.SELECTED:
            return
        elif argc == 1 and args[0] == PianoRollCanvas.ALL:
            ids = self._rects.keys()
        else:
            ids = args

        for id in ids:
            self.itemconfig(id, fill=PianoRollCanvas.SEL_FILL_COLOR,
                outline=PianoRollCanvas.SEL_FILL_COLOR)
            self._selected.add(id)

    def deselect_rects(self, *args):
        argc = len(args)
        if argc == 0:
            return
        if (argc == 1 and args[0] == PianoRollCanvas.ALL or
            args[0] == PianoRollCanvas.SELECTED):
            ids = self._selected
        else:
            ids = args

        for id in ids:
            self.itemconfig(id, fill=PianoRollCanvas.NORMAL_FILL_COLOR,
                outline=PianoRollCanvas.NORMAL_OUTLINE_COLOR)
            self._selected.remove(id)

    def remove_rects(self, *args):
        argc = len(args)
        if argc == 0:
            return
        if argc == 1 and args[0] == PianoRollCanvas.SELECTED:
            ids = self._selected
        elif argc == 1 and args[0] == PianoRollCanvas.ALL:
            ids = self._rects.keys()
        else:
            ids = args

        for id in ids:
            del self._rects[id]
            self.delete(id)

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