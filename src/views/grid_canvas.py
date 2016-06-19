import math
from Tkinter import *
from include.custom_canvas import CustomCanvas
from ..note import Note
from ..note_list import NoteList
from ..rect import Rect
from ..helper import dummy, px_to_tick
from ..const import (
    KEYS_IN_OCTAVE, KEYS_IN_LAST_OCTAVE,
    KEY_PATTERN)


class GridCanvas(CustomCanvas):

    SEL = -1
    ALL = -2

    LAYER_SEL_REGION = 0
    LAYER_RECT = 1
    LAYER_VL = 2
    LAYER_HL = 3
    LAYER_SHARP_ROW = 4

    CLICKED_ON_EMPTY_AREA = 0
    CLICKED_ON_UNSELECTED_RECT = 1
    CLICKED_ON_SELECTED_RECT = 2
    CLICKED_CTRL_ON_SELECTED_RECT = 3

    TOOL_SEL = 0
    TOOL_PEN = 1
    TOOL_ERASER = 2

    COLOR_LINE_NORMAL = "#CCCCCC"
    COLOR_LINE_BAR = "#000000"
    COLOR_OUTLINE_NORMAL = "#000000"
    COLOR_OUTLINE_SEL = "#FF0000"
    COLOR_FILL_NORMAL = "#FF0000"
    COLOR_FILL_SEL = "#990000"
    COLOR_SHARP_ROW = "#F1F3F3"

    def __init__(self, parent, gstate, dirty_cb=dummy, **kwargs):
        CustomCanvas.__init__(self, parent, **kwargs)
        self.parent = parent

        self.xview_moveto(0)
        self.yview_moveto(0)

        self._init_data(gstate, dirty_cb)
        self._init_ui()
        self._bind_event_handlers()

    def _init_ui(self):
        self.config(width=480, height=384, bg='white',
            bd=2, relief=SUNKEN)

    def _init_data(self, gstate, dirty_cb):
        self.note_list = NoteList(on_state_change=dirty_cb)
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

        if self._tool == GridCanvas.TOOL_SEL:
            if id == None:
                self.deselect_notes(GridCanvas.SEL)
                self._click_type = GridCanvas.CLICKED_ON_EMPTY_AREA
            elif id not in self.note_list.selected_ids():
                self.deselect_notes(GridCanvas.SEL)
                self.select_notes(id)
                self._click_type = GridCanvas.CLICKED_ON_UNSELECTED_RECT
            else:
                self._click_type = GridCanvas.CLICKED_ON_SELECTED_RECT

        elif self._tool == GridCanvas.TOOL_PEN:
            grid_height = self._gstate.height(zoom=False)
            cell_width = self._gstate.cell_width(zoom=False)
            cell_height = self._gstate.cell_height(zoom=False)
            cell_width_z = self._gstate.cell_width()
            cell_height_z = self._gstate.cell_height()

            self.deselect_notes(GridCanvas.ALL)

            canvasx = self.canvasx(event.x)
            canvasy = self.canvasy(event.y)

            if self._gstate.contains(canvasx, canvasy):
                x = cell_width * int(canvasx / cell_width_z)
                y = cell_height * int(canvasy / cell_height_z)

                midinumber = int((grid_height - y) / cell_height)
                velocity = 100
                onset =  px_to_tick(x)
                dur = px_to_tick(cell_width)
                note = Note(midinumber, velocity, onset, dur, selected=True)
                self.add_note(note)

        elif self._tool == GridCanvas.TOOL_ERASER:
            self.deselect_notes(GridCanvas.SEL)
            if id != None: self.remove_notes(id)

        self._click_pos = (event.x, event.y)
        self._notes_on_click = self.note_list.copy_selected()
        self._selection_bounds = self._calc_selection_bounds()

        self.parent.focus_set()

    def _on_bttnone_ctrl(self, event):
        if self._tool == GridCanvas.TOOL_SEL:
            id = self._rect_at(event.x, event.y)

            if id == None:
                self._click_type = GridCanvas.CLICKED_ON_EMPTY_AREA
            elif id not in self.note_list.selected_ids():
                self.select_notes(id)
                self._notes_on_click = self.note_list.copy_selected()
                self._selection_bounds = self._calc_selection_bounds()
                self._click_type = GridCanvas.CLICKED_ON_UNSELECTED_RECT
            else:
                self.deselect_notes(id)
                self._notes_on_click = self.note_list.copy_selected()
                self._selection_bounds = self._calc_selection_bounds()
                self._click_type = GridCanvas.CLICKED_CTRL_ON_SELECTED_RECT

            self._click_pos = (event.x, event.y)

    def _on_bttnone_release(self, event):
        dragged = (self._click_pos[0] - event.x != 0 or self._click_pos[1] - event.y != 0)
        if (len(self.note_list.selected()) > 1 and self._click_type ==
            GridCanvas.CLICKED_ON_SELECTED_RECT and not dragged):
            self.deselect_notes(GridCanvas.SEL)
            self.select_notes(self._rect_at(event.x, event.y))

        elif (self._tool == GridCanvas.TOOL_SEL == 0 and self._click_type ==
            GridCanvas.CLICKED_ON_EMPTY_AREA and dragged):
            sel_region_id = self.find_withtags('selection_region')[0]
            coords = self.coords(sel_region_id)
            overlapping = self.find_overlapping(*coords)
            rects = self.find_withtags('rect')
            overlapping_rects = set(overlapping).intersection(rects)
            self.select_notes(*overlapping_rects)
            self._notes_on_click = self.note_list.copy_selected()
            self.delete(sel_region_id)

    def _on_bttnone_motion(self, event):
        if self._tool == GridCanvas.TOOL_SEL:
            if (len(self.note_list.selected()) > 0 and self._click_type !=
                GridCanvas.CLICKED_ON_EMPTY_AREA):
                self._drag_notes(event.x, event.y)
                self._update_note_ids(self._draw_notes(*self.note_list.selected()))
            elif self._click_type == GridCanvas.CLICKED_ON_EMPTY_AREA:
                self.delete(*self.find_withtags('selection_region'))
                self._draw_selection_region(event.x, event.y)

    def _draw(self):
        self._draw_lines()
        self._draw_sharp_rows()

        visible_notes = filter(lambda note:  self._is_note_visible(note), self.note_list.notes)
        self._update_note_ids(self._draw_notes(*visible_notes))

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
            color = GridCanvas.COLOR_LINE_NORMAL
            self.add_to_layer(
                GridCanvas.LAYER_HL, self.create_line, (x1, y, x2, y),
                fill=color, tags=('line', 'horizontal'))

    def _draw_vertical_lines(self):
        grid_width = self._gstate.width()
        grid_height = self._gstate.height()
        bar_width = self._gstate.bar_width()
        cell_width = self._gstate.max_cell_width()
        y1 = self._visibleregion[1]
        y2 = self.canvasy(y1 + min(self._visibleregion[3], grid_height))

        bars_start = int(self._visibleregion[0] / bar_width)
        bars = int(min(self._visibleregion[2], grid_width) / bar_width) + 1

        for n in range(bars_start, bars_start + int(math.ceil(bars))):
            x_offset = n * bar_width
            x_left = grid_width - x_offset
            lines_per_bar = int(min(bar_width, x_left) / cell_width)
            for i in range(lines_per_bar):
                x = i * cell_width + x_offset + cell_width
                self.add_to_layer(GridCanvas.LAYER_VL,
                    self.create_line, (x, y1, x, y2),
                    fill=GridCanvas.COLOR_LINE_NORMAL,
                    tags=('line', 'vertical'))

        for i in range(bars_start, bars_start + int(math.floor(bars))):
            x = i * bar_width
            self.add_to_layer(GridCanvas.LAYER_VL,
                self.create_line, (x, y1, x, y2),
                fill=GridCanvas.COLOR_LINE_BAR,
                tags=('line', 'vertical'))

    def _draw_sharp_rows(self):
        pattern = KEY_PATTERN[::-1]
        vr_width = self._visibleregion[2]
        grid_width = self._gstate.width()
        cell_height = self._gstate.cell_height()

        x1 = 0
        x2 = min(grid_width, vr_width)
        for row in range(128):
            i = ((row + KEYS_IN_OCTAVE - KEYS_IN_LAST_OCTAVE) %
                KEYS_IN_OCTAVE)
            key = pattern[i]
            if key == '0':
                y1 = row * cell_height
                y2 = y1 + cell_height
                coords = (x1, y1, x2, y2)
                self.add_to_layer(
                    GridCanvas.LAYER_SHARP_ROW, self.create_rectangle,
                    coords, fill=GridCanvas.COLOR_SHARP_ROW, width=0,
                    tags='sharp_row')

    def _draw_notes(self, *notes):
        old_ids = []
        new_ids = []

        for note in notes:
            rect = note.rect()
            x1 = rect.left * self._gstate.zoomx
            y1 = rect.top * self._gstate.zoomy
            x2 = x1 + rect.width * self._gstate.zoomx
            y2 = y1 + rect.height * self._gstate.zoomy
            coords = (x1, y1, x2, y2)

            outline_color = (GridCanvas.COLOR_OUTLINE_SEL if
                note.selected else GridCanvas.COLOR_OUTLINE_NORMAL)
            fill_color = (GridCanvas.COLOR_FILL_SEL if
                note.selected else GridCanvas.COLOR_FILL_NORMAL)

            new_id = self.add_to_layer(
                GridCanvas.LAYER_RECT, self.create_rectangle,
                coords, outline=outline_color,
                fill=fill_color, tags='rect')

            old_ids.append(note.id)
            new_ids.append(new_id)

        return zip(old_ids, new_ids)

    def _draw_selection_region(self, mousex, mousey):
        x1 = self.canvasx(self._click_pos[0])
        y1 = self.canvasy(self._click_pos[1])
        x2 = self.canvasx(mousex)
        y2 = self.canvasy(mousey)

        coords = (x1, y1, x2, y2)
        self.add_to_layer(GridCanvas.LAYER_SEL_REGION,
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
            self.note_list.from_id(old_id).id = new_id
            if self.note_list.from_id(new_id).selected:
                self._notes_on_click.from_id(old_id).id = new_id
            if old_id:
                self.delete(old_id)

    def _is_note_visible(self, note):
        visibleregion_rect = Rect(*self._visibleregion)
        note_rect = note.rect().xscale(
            self._gstate.zoomx).yscale(
            self._gstate.zoomy)
        return visibleregion_rect.collide_rect(note_rect)

    def _calc_selection_bounds(self):
        selected_notes = self.note_list.selected()
        if not selected_notes:
            return None

        selected_rects = [note.rect() for note in selected_notes]
        leftmost = sorted(selected_rects, key=lambda r: r.left)[0]
        topmost = sorted(selected_rects, key=lambda r: r.top)[0]
        rightmost = sorted(selected_rects, key=lambda r: r.right, reverse=True)[0]
        bottommost = sorted(selected_rects, key=lambda r: r.bottom, reverse=True)[0]

        left = leftmost.left
        top = topmost.top
        right = rightmost.right
        bottom = bottommost.bottom

        return (left, top, right, bottom)

    def _drag_notes(self, mousex, mousey):
        grid_height = self._gstate.height(zoom=False)
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
            note = self.note_list.from_id(before.id)
            before_rect = before.rect()
            note.onset = px_to_tick(before_rect.left + dx)
            note.midinumber = int((grid_height -
                before_rect.top - dy) / cell_height)

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
        self.delete(*self.find_withtags('sharp_row'))
        self._draw_lines()
        self._draw_sharp_rows()
        self._adjust_layers()

    def _on_timesig_change(self):
        self._update_scrollregion()
        self.delete(*self.find_withtags('line'))
        self.delete(*self.find_withtags('sharp_row'))
        self._draw_lines()
        self._draw_sharp_rows()

    def get_note_list(self):
        return self.note_list.copy()

    def set_tool(self, value):
        self._tool = value

    def add_note(self, note):
        note.id = self._draw_notes(note)[0][1]
        self.note_list.add(note)
        self._notes_on_click.add(note)

    def remove_notes(self, *args):
        argc = len(args)
        if argc == 0:
            return
        if argc == 1 and args[0] in [GridCanvas.SEL, 'sel']:
            notes = self.note_list.copy_selected()
        elif argc == 1 and args[0] in [GridCanvas.ALL, 'all']:
            notes = self.note_list.copy()
        else:
            notes = NoteList((self.note_list.from_id(id) for id in args))

        for note in notes:
            self.note_list.remove(note)
            self.delete(note.id)

    def select_notes(self, *args):
        argc = len(args)
        if argc == 0:
            return
        if argc == 1 and args[0] == [GridCanvas.SEL, 'sel']:
            return
        elif argc == 1 and args[0] in [GridCanvas.ALL, 'all']:
            notes = self.note_list
        else:
            notes = (self.note_list.from_id(id) for id in args)

        for note in notes:
            self.itemconfig(note.id, fill=GridCanvas.COLOR_FILL_SEL,
                            outline=GridCanvas.COLOR_OUTLINE_SEL)
            note.selected = True

    def deselect_notes(self, *args):
        argc = len(args)
        if argc == 0:
            return
        if (argc == 1 and args[0] in
            [GridCanvas.SEL, GridCanvas.ALL, 'all', 'sel']):
            notes = self.note_list.selected()
        else:
            notes = (self.note_list.from_id(id) for id in args)

        for note in notes:
            self.itemconfig(note.id, fill=GridCanvas.COLOR_FILL_NORMAL,
                            outline=GridCanvas.COLOR_OUTLINE_NORMAL)
            note.selected = False

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