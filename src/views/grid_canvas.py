import math
from Tkinter import *
from ..note import Note
from ..note_list import NoteList
from ..rect import Rect
from include.custom_canvas import CustomCanvas


class GridCanvas(CustomCanvas):

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

    def __init__(self, parent, gstate, **kwargs):
        CustomCanvas.__init__(self, parent, **kwargs)
        self.parent = parent

        self.xview_moveto(0)
        self.yview_moveto(0)

        self._init_data(gstate)
        self._init_ui()
        self._bind_event_handlers()

    def _init_ui(self):
        self.config(width=512, height=384, bg='white',
            bd=2, relief=SUNKEN)

    def _init_data(self, gstate):
        self._notes = NoteList()
        self._notes_on_click = NoteList()
        self._selection_bounds = None

        self._click_pos = None
        self._click_type = GridCanvas.CLICKED_ON_EMPTY_AREA

        self._tool = 0
        self._gstate = gstate

        vs_height = int(self.config()['height'][4])
        vs_width = int(self.config()['width'][4])
        sr_width = self._gstate.width()
        sr_height = self._gstate.height()
        self._visibleregion = [0, 0, vs_width, vs_height]
        scrollregion = (0, 0, sr_width, sr_height)
        self.config(scrollregion=scrollregion)

    def _bind_event_handlers(self):
        self.bind('<ButtonPress-1>', self._on_bttnone_press)
        self.bind('<ButtonRelease-1>', self._on_bttnone_release)
        self.bind('<B1-Motion>', self._on_bttnone_motion)
        self.bind('<Control-1>', self._on_bttnone_ctrl)
        self.bind('<Configure>', self._on_window_resize)

    def _on_bttnone_press(self, event):
        id = self._rect_at(event.x, event.y)

        if self._tool == GridCanvas.SEL_TOOL:
            if id == None:
                self.deselect_notes(GridCanvas.SELECTED)
                self._click_type = GridCanvas.CLICKED_ON_EMPTY_AREA
            elif id not in self._notes.selected_ids():
                self.deselect_notes(GridCanvas.SELECTED)
                self.select_notes(id)
                self._click_type = GridCanvas.CLICKED_ON_UNSELECTED_RECT
            else:
                self._click_type = GridCanvas.CLICKED_ON_SELECTED_RECT

        elif self._tool == GridCanvas.PEN_TOOL:
            self.deselect_notes(GridCanvas.SELECTED)
            canvasx = self.canvasx(event.x)
            canvasy = self.canvasy(event.y)
            if self._gstate.contains(canvasx, canvasy):
                rect = self._calc_note_rect(canvasx, canvasy)
                new_note = Note(GridCanvas.NO_ID, rect, True)
                new_note.id = self._draw_notes(new_note)[0][1]
                self._notes.add(new_note)
                self._notes_on_click.add(new_note)

        elif self._tool == GridCanvas.ERASER_TOOL:
            self.deselect_notes(GridCanvas.SELECTED)
            if id != None: self.remove_notes(id)

        self._click_pos = (event.x, event.y)
        self._notes_on_click = self._notes.copy_selected()
        self._selection_bounds = self._calc_selection_bounds()

        self.parent.focus_set()

    def _on_bttnone_ctrl(self, event):
        if self._tool == GridCanvas.SEL_TOOL:
            id = self._rect_at(event.x, event.y)

            if id == None:
                self._click_type = GridCanvas.CLICKED_ON_EMPTY_AREA
            elif id not in self._notes.selected_ids():
                self.select_notes(id)
                self._notes_on_click = self._notes.copy_selected()
                self._selection_bounds = self._calc_selection_bounds()
                self._click_type = GridCanvas.CLICKED_ON_UNSELECTED_RECT
            else:
                self.deselect_notes(id)
                self._notes_on_click = self._notes.copy_selected()
                self._selection_bounds = self._calc_selection_bounds()
                self._click_type = GridCanvas.CLICKED_CTRL_ON_SELECTED_RECT

            self._click_pos = (event.x, event.y)

    def _on_bttnone_release(self, event):
        dragged = (self._click_pos[0] - event.x != 0 or self._click_pos[1] - event.y != 0)
        if (len(self._notes.selected()) > 1 and self._click_type ==
            GridCanvas.CLICKED_ON_SELECTED_RECT and not dragged):
            self.deselect_notes(GridCanvas.SELECTED)
            self.select_notes(self._rect_at(event.x, event.y))

        elif (self._tool == GridCanvas.SEL_TOOL == 0 and self._click_type ==
            GridCanvas.CLICKED_ON_EMPTY_AREA and dragged):
            sel_region_id = self.find_withtags('selection_region')[0]
            coords = self.coords(sel_region_id)
            overlapping = self.find_overlapping(*coords)
            rects = self.find_withtags('rect')
            overlapping_rects = set(overlapping).intersection(rects)
            self.select_notes(*overlapping_rects)
            self._notes_on_click = self._notes.copy_selected()
            self.delete(sel_region_id)

    def _on_bttnone_motion(self, event):
        if self._tool == GridCanvas.SEL_TOOL:
            if (len(self._notes.selected()) > 0 and self._click_type !=
                GridCanvas.CLICKED_ON_EMPTY_AREA):
                self._drag_notes(event.x, event.y)
                self._update_note_ids(self._draw_notes(*self._notes.selected()))
            elif self._click_type == GridCanvas.CLICKED_ON_EMPTY_AREA:
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
        cell_height = self._gstate.cell_height()
        visibleregion_height = self._visibleregion[3]
        grid_height = self._gstate.height()
        n = int(min(visibleregion_height, grid_height) / cell_height) + 1

        x1 = self.canvasx(0)
        x2 = min(self.canvasx(self._visibleregion[2]), self._gstate.width())

        yorigin = self.canvasy(0)
        offset = cell_height * math.ceil(yorigin / cell_height)

        for j in range(n):
            y = j * cell_height + offset
            color = GridCanvas.NORMAL_LINE_COLOR
            self.add_to_layer(GridCanvas.HL_LAYER,
                self.create_line, (x1, y, x2, y),
                fill=color, tags=('line', 'horizontal'))

    def _draw_vertical_lines(self):
        grid_width = self._gstate.width()
        grid_height = self._gstate.height()
        bar_width = self._gstate.bar_width()
        cell_width = self._gstate.max_cell_width()
        y1 = self._visibleregion[1]
        y2 = self.canvasy(y1 + min(self._visibleregion[3], grid_height))

        bars_start = int(self._visibleregion[0] / bar_width)
        bars = int(math.ceil((min(self._visibleregion[2], grid_width) +
            bar_width) / bar_width))

        for n in range(bars_start, bars_start + bars):
            x_offset = n * bar_width
            x_left = grid_width - x_offset
            lines_per_bar = int(min(bar_width, x_left) / cell_width)
            for i in range(lines_per_bar):
                x = i * cell_width + x_offset + cell_width
                self.add_to_layer(GridCanvas.VL_LAYER,
                    self.create_line, (x, y1, x, y2),
                    fill=GridCanvas.NORMAL_LINE_COLOR,
                    tags=('line', 'vertical'))

        for i in range(bars_start, bars + bars_start):
            x = i * bar_width
            self.add_to_layer(GridCanvas.VL_LAYER,
                self.create_line, (x, y1, x, y2),
                fill=GridCanvas.BAR_LINE_COLOR,
                tags=('line', 'vertical'))

    def _draw_notes(self, *notes):
        old_ids = []
        new_ids = []

        for note in notes:
            x1 = note.rect[0] * self._gstate.zoomx
            y1 = note.rect[1] * self._gstate.zoomy
            x2 = x1 + note.rect[2] * self._gstate.zoomx
            y2 = y1 + note.rect[3] * self._gstate.zoomy
            coords = (x1, y1, x2, y2)

            outline_color = (GridCanvas.SEL_OUTLINE_COLOR if note.selected else
                GridCanvas.NORMAL_OUTLINE_COLOR)
            fill_color = (GridCanvas.SEL_FILL_COLOR if note.selected else
                GridCanvas.NORMAL_FILL_COLOR)

            new_id = self.add_to_layer(GridCanvas.RECT_LAYER, self.create_rectangle,
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
        self.add_to_layer(GridCanvas.SEL_REGION_LAYER,
            self.create_rectangle, coords, fill='blue', outline='blue',
            stipple='gray12', tags='selection_region')

    def _update_scrollregion(self):
        visibleregion_width = self._visibleregion[2]
        visibleregion_height = self._visibleregion[3]

        scrollregion_width = max(self._gstate.width(), visibleregion_width)
        scrollregion_height = max(self._gstate.height(), visibleregion_height) + 1

        self.config(scrollregion=(0, 0, scrollregion_width, scrollregion_height))

    def _update_visibleregion(self):
        bd = int(self.config()['borderwidth'][4])
        vr_left = self.canvasx(0) + bd
        vr_top = self.canvasy(0) + bd
        vr_width = self.winfo_width() - bd * 2
        vr_height = self.winfo_height() - bd * 2
        self._visibleregion = (vr_left, vr_top, vr_width, vr_height)

    def _update_note_ids(self, ids):
        for old_id, new_id in ids:
            self._notes.from_id(old_id).id = new_id
            if self._notes.from_id(new_id).selected:
                self._notes_on_click.from_id(old_id).id = new_id
            if old_id != GridCanvas.NO_ID:
                self.delete(old_id)

    def _is_note_visible(self, note):
        visibleregion_rect = Rect(*self._visibleregion)
        note_rect = Rect(*note.rect).xscale(
            self._gstate.zoomx).yscale(
            self._gstate.zoomy)
        return visibleregion_rect.collide_rect(note_rect)

    def _calc_note_rect(self, canvasx, canvasy):
        cell_width = self._gstate.cell_width(zoom=False)
        cell_height = self._gstate.cell_height(zoom=False)
        cell_width_z = self._gstate.cell_width()
        cell_height_z = self._gstate.cell_height()

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
        cell_width = self._gstate.cell_width(zoom=False)
        cell_height = self._gstate.cell_height(zoom=False)
        cell_width_z = self._gstate.cell_width()
        cell_height_z = self._gstate.cell_height()

        dx = cell_width * round(float(mousex - self._click_pos[0]) / cell_width_z)
        dy = cell_height * round(float(mousey - self._click_pos[1]) / cell_height_z)

        if self._selection_bounds[0] + dx < 0:
            dx = -self._selection_bounds[0]
        elif self._selection_bounds[2] + dx >= self._gstate.width(zoom=False):
            grid_right = self._gstate.width(False)
            sel_right = self._selection_bounds[2]
            row = self._gstate.row(grid_right - sel_right, zoom=False)
            dx = cell_width * row

        if self._selection_bounds[1] + dy < 0:
            dy = -self._selection_bounds[1]
        elif self._selection_bounds[3] + dy >= self._gstate.height(zoom=False):
            grid_bottom  = self._gstate.height(False)
            sel_bottom = self._selection_bounds[3]
            col = self._gstate.col(grid_bottom - sel_bottom, zoom=False)
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

    def _on_window_resize(self, event):
        self._update_scrollregion()
        self._update_visibleregion()
        self.delete(*self.find_withtags('line'))
        self._draw()

    def _on_subdiv_change(self):
        self.delete(*self.find_withtags('line', 'vertical'))
        self._draw_lines()
        self._adjust_layers()

    def _on_zoom_change(self):
        self._update_scrollregion()
        self._update_visibleregion()
        self.delete(ALL)
        self._draw()

    def _on_length_change(self):
        self._update_scrollregion()
        self._update_visibleregion()
        self.delete(*self.find_withtags('line'))
        self._draw_lines()
        self._adjust_layers()

    def _on_timesig_change(self):
        self._update_scrollregion()
        self.delete(*self.find_withtags('line'))
        self._draw_lines()

    def get_note_list(self):
        return self._notes.copy()

    def set_tool(self, value):
        self._tool = value

    def select_notes(self, *args):
        argc = len(args)
        if argc == 0:
            return
        if argc == 1 and args[0] == GridCanvas.SELECTED:
            return
        elif argc == 1 and args[0] == GridCanvas.ALL:
            notes = self._notes
        else:
            notes = (self._notes.from_id(id) for id in args)

        for note in notes:
            self.itemconfig(note.id, fill=GridCanvas.SEL_FILL_COLOR,
                outline=GridCanvas.SEL_OUTLINE_COLOR)
            note.selected = True

    def deselect_notes(self, *args):
        argc = len(args)
        if argc == 0:
            return
        if (argc == 1 and args[0] == GridCanvas.ALL or
            args[0] == GridCanvas.SELECTED):
            notes = self._notes.selected()
        else:
            notes = (self._notes.from_id(id) for id in args)

        for note in notes:
            self.itemconfig(note.id, fill=GridCanvas.NORMAL_FILL_COLOR,
                outline=GridCanvas.NORMAL_OUTLINE_COLOR)
            note.selected = False

    def remove_notes(self, *args):
        argc = len(args)
        if argc == 0:
            return
        if argc == 1 and args[0] == GridCanvas.SELECTED:
            notes = self._notes.selected()
        elif argc == 1 and args[0] == GridCanvas.ALL:
            notes = self._notes
        else:
            notes = (self._notes.from_id(id) for id in args)

        for note in notes:
            self._notes.remove(note)
            self.delete(note.id)

    def on_update(self, new_gstate):
        diff = self._gstate - new_gstate
        self._gstate = new_gstate

        if any(x in diff for x in ['beat_count', 'beat_unit']):
            self._on_timesig_change()
        if 'subdiv' in diff:
            self._on_subdiv_change()
        if any(x in diff for x in ['zoomx', 'zoomy']):
            self._on_zoom_change()
        if 'length' in diff:
            self._on_length_change()

    def xview(self, *args):
        self.delete(ALL)
        CustomCanvas.xview(self, *args)
        self._update_visibleregion()
        self._draw()

    def yview(self, *args):
        self.delete(*self.find_withtags('line'))
        CustomCanvas.yview(self, *args)
        self._update_visibleregion()
        self._draw()