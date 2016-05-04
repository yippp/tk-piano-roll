import math
from Tkinter import *
from ..grid import Grid
from ..note import Note
from ..note_list import NoteList
from ..rect import Rect
from include.custom_canvas import CustomCanvas


class PianoRollCanvas(CustomCanvas):

    NO_ID = -1

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
        CustomCanvas.__init__(self, parent, width=512, height=384, bg='white', **kwargs)
        self.parent = parent

        self._init_data()
        self._bind_event_handlers()
        self._draw_lines()

    def _init_data(self):
        self._notes = NoteList()
        self._notes_on_click = NoteList()
        self._selection_bounds = None

        self._click_pos = None
        self._click_type = PianoRollCanvas.CLICKED_ON_EMPTY_AREA

        self._tool = 0
        self._grid = Grid()

        scrollregion_height = self._grid.height()
        self._scrollregion = [0, 0, 512, scrollregion_height]
        self._visibleregion = [0, 0, 512, 384]
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
                self.deselect_notes(PianoRollCanvas.SELECTED)
                self._click_type = PianoRollCanvas.CLICKED_ON_EMPTY_AREA
            elif id not in self._notes.selected_ids():
                self.deselect_notes(PianoRollCanvas.SELECTED)
                self.select_notes(id)
                self._click_type = PianoRollCanvas.CLICKED_ON_UNSELECTED_RECT
            else:
                self._click_type = PianoRollCanvas.CLICKED_ON_SELECTED_RECT

        elif self._tool == PianoRollCanvas.PEN_TOOL:
            self.deselect_notes(PianoRollCanvas.SELECTED)
            canvasx = self.canvasx(event.x)
            canvasy = self.canvasy(event.y)
            if self._grid.contains(canvasx, canvasy):
                rect = self._calc_note_rect(canvasx, canvasy)
                new_note = Note(PianoRollCanvas.NO_ID, rect, True)
                new_note.id = self._draw_notes(new_note)[0][1]
                self._notes.add(new_note)
                self._notes_on_click.add(new_note)

        elif self._tool == PianoRollCanvas.ERASER_TOOL:
            self.deselect_notes(PianoRollCanvas.SELECTED)
            if id != None: self.remove_notes(id)

        self._click_pos = (event.x, event.y)
        self._notes_on_click = self._notes.copy_selected()
        self._selection_bounds = self._calc_selection_bounds()

        self.parent.focus_set()

    def _on_bttnone_ctrl(self, event):
        if self._tool == PianoRollCanvas.SEL_TOOL:
            id = self._rect_at(event.x, event.y)

            if id == None:
                self._click_type = PianoRollCanvas.CLICKED_ON_EMPTY_AREA
            elif id not in self._notes.selected_ids():
                self.select_notes(id)
                self._notes_on_click = self._notes.copy_selected()
                self._selection_bounds = self._calc_selection_bounds()
                self._click_type = PianoRollCanvas.CLICKED_ON_UNSELECTED_RECT
            else:
                self.deselect_notes(id)
                self._notes_on_click = self._notes.copy_selected()
                self._selection_bounds = self._calc_selection_bounds()
                self._click_type = PianoRollCanvas.CLICKED_CTRL_ON_SELECTED_RECT

            self._click_pos = (event.x, event.y)

    def _on_bttnone_release(self, event):
        dragged = (self._click_pos[0] - event.x != 0 or self._click_pos[1] - event.y != 0)
        if (len(self._notes.selected()) > 1 and self._click_type ==
            PianoRollCanvas.CLICKED_ON_SELECTED_RECT and not dragged):
            self.deselect_notes(PianoRollCanvas.SELECTED)
            self.select_notes(self._rect_at(event.x, event.y))

        elif (self._tool == PianoRollCanvas.SEL_TOOL == 0 and self._click_type ==
            PianoRollCanvas.CLICKED_ON_EMPTY_AREA and dragged):
            sel_region_id = self.find_withtags('selection_region')[0]
            coords = self.coords(sel_region_id)
            overlapping = self.find_overlapping(*coords)
            rects = self.find_withtags('rect')
            overlapping_rects = set(overlapping).intersection(rects)
            self.select_notes(*overlapping_rects)
            self._notes_on_click = self._notes.copy_selected()
            self.delete(sel_region_id)

    def _on_bttnone_motion(self, event):
        if self._tool == PianoRollCanvas.SEL_TOOL:
            if (len(self._notes.selected()) > 0 and self._click_type !=
                PianoRollCanvas.CLICKED_ON_EMPTY_AREA):
                self._drag_notes(event.x, event.y)
                visible_notes = filter(lambda note: self._is_note_visible(note),
                    self._notes.selected())
                self._update_note_ids(self._draw_notes(*visible_notes))
            elif self._click_type == PianoRollCanvas.CLICKED_ON_EMPTY_AREA:
                self.delete(*self.find_withtags('selection_region'))
                self._draw_selection_region(event.x, event.y)

    def _draw(self):
        visible_notes = filter(lambda note: self._is_note_visible(note), self._notes.notes)
        self._update_note_ids(self._draw_notes(*visible_notes))
        self._draw_lines()

    def _draw_lines(self):
        self._draw_horizontal_lines()
        self._draw_vertical_lines()

    def _draw_horizontal_lines(self):
        cell_height = self._grid.cell_height()
        n = int(self._visibleregion[3] / cell_height) + 1

        x1 = self.canvasx(0)
        x2 = min(self.canvasx(self._visibleregion[2]), self._grid.width())

        yorigin = self.canvasy(0)
        offset = cell_height * math.ceil(yorigin / cell_height)

        for j in range(n):
            y = j * cell_height + offset
            color = PianoRollCanvas.NORMAL_LINE_COLOR
            self.add_to_layer(PianoRollCanvas.HL_LAYER,
                self.create_line, (x1, y, x2, y),
                fill=color, tags=('line', 'horizontal'))

    def _draw_vertical_lines(self):
        visibleregion_width = self._visibleregion[2]
        visibleregion_height = self._visibleregion[3]

        cell_width = self._grid.max_cell_width()

        n = int(min(self._grid.width(), visibleregion_width) / cell_width) + 1

        y1 = self.canvasy(0)
        y2 = self.canvasy(visibleregion_height)
        xorigin = self.canvasx(0)

        offset = cell_width * math.ceil(xorigin / cell_width)

        for i in range(n):
            x = i * cell_width + offset
            if x % self._grid.bar_width() == 0:
                color = PianoRollCanvas.BAR_LINE_COLOR
            else:
                color = PianoRollCanvas.NORMAL_LINE_COLOR

            self.add_to_layer(PianoRollCanvas.VL_LAYER,
                self.create_line, (x, y1, x, y2),
                fill=color, tags=('line', 'vertical'))

    def _draw_notes(self, *notes):
        old_ids = []
        new_ids = []

        for note in notes:
            x1 = note.rect[0] * self._grid.zoomx
            y1 = note.rect[1] * self._grid.zoomy
            x2 = x1 + note.rect[2] * self._grid.zoomx
            y2 = y1 + note.rect[3] * self._grid.zoomy
            coords = (x1, y1, x2, y2)

            outline_color = (PianoRollCanvas.SEL_OUTLINE_COLOR if note.selected else
                PianoRollCanvas.NORMAL_OUTLINE_COLOR)
            fill_color = (PianoRollCanvas.SEL_FILL_COLOR if note.selected else
                PianoRollCanvas.NORMAL_FILL_COLOR)

            new_id = self.add_to_layer(PianoRollCanvas.RECT_LAYER, self.create_rectangle,
                coords, outline=outline_color, fill=fill_color, tags='rect')

            old_ids.append(note.id)
            new_ids.append(new_id)

        return zip(old_ids, new_ids)

    def _draw_selection_region(self, mousex, mousey):
        x1 = self.canvasx(self._click_pos[0])
        y1 = self.canvasy(self._click_pos[1])
        x2 = self.canvasx(mousex)
        y2 = self.canvasy(mousey)

        coords = (x1, y1, x2, y2)
        self.add_to_layer(PianoRollCanvas.SEL_REGION_LAYER,
            self.create_rectangle, coords, fill='blue', outline='blue',
            stipple='gray12', tags='selection_region')

    def _update_regions(self, event):
        self._update_visibleregion()
        self._update_scrollregion()

    def _update_note_ids(self, ids):
        for old_id, new_id in ids:
            self._notes.from_id(old_id).id = new_id
            if self._notes.from_id(new_id).selected:
                self._notes_on_click.from_id(old_id).id = new_id
            if old_id != PianoRollCanvas.NO_ID:
                self.delete(old_id)

    def _update_scrollregion(self):
        visibleregion_width = self._visibleregion[2]
        scrollregion_width = max(self._grid.width(), visibleregion_width)
        scrollregion_height = self._grid.height()
        self.config(scrollregion=(0, 0, scrollregion_width, scrollregion_height))

    def _update_visibleregion(self):
        self._visibleregion[2] = self.winfo_width() - 2
        self._visibleregion[3] = self.winfo_height() - 2

        self.delete(*self.find_withtags('line'))
        self._draw_lines()

    def _is_note_visible(self, note):
        visibleregion_rect = Rect(*self._visibleregion)
        note_rect = Rect(*note.rect).xscale(self._grid.zoomx).yscale(self._grid.zoomy)
        return visibleregion_rect.collide_rect(note_rect)

    def _calc_note_rect(self, canvasx, canvasy):
        cell_width = self._grid.cell_width(False)
        cell_height = self._grid.cell_height(False)
        cell_width_z = self._grid.cell_width()
        cell_height_z = self._grid.cell_height()

        rect_x = cell_width * int(canvasx / cell_width_z)
        rect_y = cell_height * int(canvasy / cell_height_z)

        return [rect_x, rect_y, cell_width, cell_height]

    def _calc_selection_bounds(self):
        selected_notes = self._notes.selected()
        if not selected_notes:
            return None

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

    def _drag_notes(self, mousex, mousey):
        cell_width = self._grid.cell_width(False)
        cell_height = self._grid.cell_height(False)
        cell_width_z = self._grid.cell_width()
        cell_height_z = self._grid.cell_height()

        dx = cell_width * round(float(mousex - self._click_pos[0]) / cell_width_z)
        dy = cell_height * round(float(mousey - self._click_pos[1]) / cell_height_z)

        if self._selection_bounds[0] + dx < 0:
            dx = -self._selection_bounds[0]
        elif self._selection_bounds[2] + dx >= self._grid.width(False):
            grid_right = self._grid.width(False)
            sel_right = self._selection_bounds[2]
            row = self._grid.row(grid_right - sel_right, False)
            dx = cell_width * row

        if self._selection_bounds[1] + dy < 0:
            dy = -self._selection_bounds[1]
        elif self._selection_bounds[3] + dy >= self._grid.height(False):
            grid_bottom  = self._grid.height(False)
            sel_bottom = self._selection_bounds[3]
            col = self._grid.col(grid_bottom - sel_bottom, False)
            dy = cell_height * col

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

    def remove_notes(self, *args):
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
        self._grid.subdiv = value
        self.delete(*self.find_withtags('line', 'vertical'))
        self._draw_lines()
        self._adjust_layers()

    def set_zoomx(self, value):
        self._grid.zoomx = value

        self._update_scrollregion()
        self.delete(ALL)
        self._draw()
        self._adjust_layers()

    def set_zoomy(self, value):
        self._grid.zoomy = value

        self._update_scrollregion()
        self.delete(ALL)
        self._draw()
        self._adjust_layers()

    def set_length(self, value):
        self._grid.length = value

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