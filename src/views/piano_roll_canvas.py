import math
from sets import Set
from Tkinter import *
from ..const import SNAP_DICT, DEFAULT_BAR_WIDTH_IN_PX
from include.custom_canvas import CustomCanvas
from include.rect import Rect

__all__ = ['PianoRollCanvas']


class _Note(object):

    def __init__(self, id, rect, selected=False):
        self.id = id
        self.rect = rect
        self.selected = selected

    def __eq__(self, other):
        return self.id == other.id and self.rect == other.rect

    def copy(self):
        return _Note(self.id, list(self.rect), self.selected)


class _NoteList(object):

    def __init__(self, notes=()):
        self.notes = list(notes)

    def __iter__(self):
        for note in self.notes:
            yield note

    def __contains__(self, arg):
        if isinstance(arg, _Note):
            return arg in self.notes
        elif isinstance(arg, (int, long)):
            return self.from_id(arg) != None

    def copy(self):
        return _NoteList([note.copy() for note in self.notes])

    def copy_selected(self):
        return _NoteList([note.copy() for note in self.selected()])

    def select(self, *ids):
        for id in ids:
            note = self.from_id(id)
            note.selected = True

    def deselect(self, *ids):
        for id in ids:
            note = self.from_id(id)
            note.selected = False

    def selected(self):
        return filter(lambda note: note.selected, self.notes)

    def ids(self):
        return [note.id for note in self.notes]

    def selected_ids(self):
        return list(Set(self.ids()).intersection([note.id for note in self.selected()]))

    def from_id(self, id):
        for note in self.notes:
            if note.id == id:
                return note

        return None

    def add(self, note):
        if not isinstance(note, _Note):
            raise ValueError

        self.notes.append(note)

    def remove(self, note):
        self.notes.remove(note)


class PianoRollCanvas(CustomCanvas):

    DEFAULT_CELL_HEIGHT_IN_PX = 10
    MIN_CELL_WIDTH_IN_PX = 20
    GRID_HEIGHT_IN_CELLS = 128

    SELECTED = -1
    ALL = -2

    SEL_REGION_LAYER = 0
    RECT_LAYER = 1
    VL_LAYER = 2
    HL_LAYER = 3

    CLICKED_ON_EMPTY_AREA = 0
    CLICKED_ON_UNSELECTED_RECT = 1
    CLICKED_ON_SELECTED_RECT = 2
    CLICKED_CTRL_ON_SELECTED_RECT = 3

    SEL_TOOL = 0
    PEN_TOOL = 1
    ERASER_TOOL = 2

    NORMAL_LINE_COLOR = "#CCCCCC"
    BAR_LINE_COLOR = "#000000"
    NORMAL_OUTLINE_COLOR = "#000000"
    SEL_OUTLINE_COLOR = "#FF0000"
    NORMAL_FILL_COLOR = "#FF0000"
    SEL_FILL_COLOR = "#990000"

    def __init__(self, parent, **kwargs):
        CustomCanvas.__init__(self, parent, width=640, height=480, bg='white', **kwargs)
        self.parent = parent

        self._init_data()
        self._bind_event_handlers()
        self._draw_lines()

    def _init_data(self):
        self._notes = _NoteList()
        self._notes_on_click = _NoteList()
        self._selection_bounds = None

        self._click_pos = None
        self._click_type = PianoRollCanvas.CLICKED_ON_EMPTY_AREA

        self._tool = 0
        self._grid_data = {
            'subdiv': SNAP_DICT.values()[0],
            'zoomx': 1,
            'zoomy': 1,
            'length': DEFAULT_BAR_WIDTH_IN_PX
        }

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
        id = self._rect_at(event.x, event.y)

        if self._tool == PianoRollCanvas.SEL_TOOL:
            if id == None:
                self.deselect_notes(*self._notes.selected_ids())
                self._click_type = PianoRollCanvas.CLICKED_ON_EMPTY_AREA
            elif id not in self._notes.selected_ids():
                self.deselect_notes(*self._notes.selected_ids())
                self.select_notes(id)
                self._click_type = PianoRollCanvas.CLICKED_ON_UNSELECTED_RECT
            else:
                self._click_type = PianoRollCanvas.CLICKED_ON_SELECTED_RECT

        elif self._tool == PianoRollCanvas.PEN_TOOL:
            self.deselect_notes(*self._notes.selected_ids())
            self._add_rect(event)

        elif self._tool == PianoRollCanvas.ERASER_TOOL:
            self.deselect_notes(*self._notes.selected_ids())
            if id != None: self.remove_rects(id)

        self._click_pos = (event.x, event.y)
        self._notes_on_click = self._notes.copy_selected()
        self._selection_bounds = self._calc_bounding_rect(*self._notes.selected_ids())

        self.parent.focus_set()

    def _on_bttnone_ctrl(self, event):
        if self._tool == PianoRollCanvas.SEL_TOOL:
            id = self._rect_at(event.x, event.y)

            if id == None:
                self._click_type = PianoRollCanvas.CLICKED_ON_EMPTY_AREA
            elif id not in self._notes.selected_ids():
                self.select_notes(id)
                self._notes_on_click = self._notes.copy_selected()
                self._selection_bounds = self._calc_bounding_rect(*self._notes.selected_ids())
                self._click_type = PianoRollCanvas.CLICKED_ON_UNSELECTED_RECT
            else:
                self.deselect_notes(id)
                self._notes_on_click = self._notes.copy_selected()
                self._selection_bounds = self._calc_bounding_rect(*self._notes.selected_ids())
                self._click_type = PianoRollCanvas.CLICKED_CTRL_ON_SELECTED_RECT

            self._click_pos = (event.x, event.y)

    def _on_bttnone_release(self, event):
        dragged = (self._click_pos[0] - event.x != 0 or self._click_pos[1] - event.y != 0)
        if (len(self._notes.selected()) > 1 and self._click_type ==
            PianoRollCanvas.CLICKED_ON_SELECTED_RECT and not dragged):
            self.deselect_notes(*self._notes.selected_ids())
            self.select_notes(self._rect_at(event.x, event.y))

        elif (self._tool == PianoRollCanvas.SEL_TOOL == 0 and self._click_type ==
            PianoRollCanvas.CLICKED_ON_EMPTY_AREA and dragged):
            sel_region_id = self.find_withtags('selection_region')[0]
            coords = self.coords(sel_region_id)
            overlapping = self.find_overlapping(*coords)
            rects = self.find_withtags('rect')
            overlapping_rects = set(overlapping).intersection(rects)
            self.select_notes(*overlapping_rects)
            self.delete(sel_region_id)

    def _on_bttnone_motion(self, event):
        if self._tool == PianoRollCanvas.SEL_TOOL:
            if (len(self._notes.selected()) > 0 and self._click_type !=
                PianoRollCanvas.CLICKED_ON_EMPTY_AREA):
                self._drag_rects(event.x, event.y)
                self.delete(*self.find_withtags('rect'))
                self._draw_rects()
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

        for note in self._notes:
            x1 = note.rect[0] * zoomx
            y1 = note.rect[1] * zoomy
            x2 = x1 + note.rect[2] * zoomx
            y2 = y1 + note.rect[3] * zoomy
            coords = (x1, y1, x2, y2)

            outline_color = (PianoRollCanvas.SEL_OUTLINE_COLOR if note.selected else
                PianoRollCanvas.NORMAL_OUTLINE_COLOR)
            fill_color = (PianoRollCanvas.SEL_FILL_COLOR if note.selected else
                PianoRollCanvas.NORMAL_FILL_COLOR)

            new_id = self.add_to_layer(PianoRollCanvas.RECT_LAYER, self.create_rectangle,
                coords, outline=outline_color, fill=fill_color, tags='rect')
            old_id = note.id

            if old_id in self._notes.selected_ids():
                self._notes_on_click.from_id(old_id).id = new_id

            note.id = new_id

    def _draw_selection_region(self, mousex, mousey):
        x1 = self.canvasx(self._click_pos[0])
        y1 = self.canvasy(self._click_pos[1])
        x2 = self.canvasx(mousex)
        y2 = self.canvasy(mousey)

        coords = (x1, y1, x2, y2)
        self.add_to_layer(PianoRollCanvas.SEL_REGION_LAYER,
            self.create_rectangle, coords, fill='blue', outline='blue',
            stipple='gray12', tags='selection_region')

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

    def _calc_bounding_rect(self, *ids):
        if not ids: return

        selected_notes = self._notes.selected()
        selected_rects = [note.rect for note in selected_notes]
        leftmost = sorted(selected_rects,   key=lambda r:   r[0]                     )[0]
        topmost = sorted(selected_rects,    key=lambda r:   r[1]                     )[0]
        rightmost = sorted(selected_rects,  key=lambda r:   r[0] + r[2], reverse=True)[0]
        bottommost = sorted(selected_rects, key=lambda r:   r[1] + r[3], reverse=True)[0]

        left = leftmost[0]
        top = topmost[1]
        right = rightmost[0] + rightmost[2]
        bottom = bottommost[1] + bottommost[3]

        return (left, top, right, bottom)

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

            rect = [rect_x, rect_y, cell_width, cell_height]
            self._notes.add(_Note(id, rect, True))

    def _drag_rects(self, mousex, mousey):
        subdiv = self._grid_data['subdiv']
        zoomx = self._grid_data['zoomx']
        zoomy = self._grid_data['zoomy']
        length = self._grid_data['length']

        scrollregion_height = self._scrollregion[3]

        cell_width = self._calc_cell_width(subdiv)
        cell_height = self._calc_cell_height()
        cell_width_z = cell_width * zoomx
        cell_height_z = cell_height * zoomy

        dx = cell_width * round(float(mousex - self._click_pos[0]) / cell_width_z)
        dy = cell_height * round(float(mousey - self._click_pos[1]) / cell_height_z)

        grid_rect = Rect(0, 0, length, scrollregion_height)

        if self._selection_bounds[0] + dx < grid_rect.left:
            dx = grid_rect.left - self._selection_bounds[0]
        elif self._selection_bounds[2] + dx >= grid_rect.right:
            dx = grid_rect.right - self._selection_bounds[2]

        if self._selection_bounds[1] + dy < grid_rect.top:
            dy = grid_rect.top - self._selection_bounds[1]
        elif self._selection_bounds[3] + dy >= grid_rect.bottom:
            dy = grid_rect.bottom - self._selection_bounds[3]

        for before in self._notes_on_click:
            note = self._notes.from_id(before.id)
            note.rect[0] = before.rect[0] + dx
            note.rect[1] = before.rect[1] + dy

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

    def select_notes(self, *args):
        argc = len(args)
        if argc == 0:
            return
        if argc == 1 and args[0] == PianoRollCanvas.SELECTED:
            return
        elif argc == 1 and args[0] == PianoRollCanvas.ALL:
            notes = self._notes
        else:
            notes = (self._notes.from_id(id) for id in args)

        for note in notes:
            self.itemconfig(note.id, fill=PianoRollCanvas.SEL_FILL_COLOR,
                outline=PianoRollCanvas.SEL_FILL_COLOR)
            note.selected = True

    def deselect_notes(self, *args):
        argc = len(args)
        if argc == 0:
            return
        if (argc == 1 and args[0] == PianoRollCanvas.ALL or
            args[0] == PianoRollCanvas.SELECTED):
            notes = self._notes.selected()
        else:
            notes = (self._notes.from_id(id) for id in args)

        for note in notes:
            self.itemconfig(note.id, fill=PianoRollCanvas.NORMAL_FILL_COLOR,
                outline=PianoRollCanvas.NORMAL_OUTLINE_COLOR)
            note.selected = False

    def remove_rects(self, *args):
        argc = len(args)
        if argc == 0:
            return
        if argc == 1 and args[0] == PianoRollCanvas.SELECTED:
            notes = self._notes.selected()
        elif argc == 1 and args[0] == PianoRollCanvas.ALL:
            notes = self._notes
        else:
            notes = (self._notes.from_id(id) for id in args)

        for note in notes:
            self._notes.remove(note)
            self.delete(note.id)

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