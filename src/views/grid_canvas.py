import math
from Tkinter import *
from include.custom_canvas import CustomCanvas
from ..note import Note
from ..note_list import NoteList
from ..rect import Rect
from ..mouse_state import MouseState
from ..helper import px_to_tick
from ..paths import (CURSOR_SEL_IMG_PATH,
    CURSOR_PEN_IMG_PATH, CURSOR_ERASER_IMG_PATH)
from ..const import (
    KEYS_IN_OCTAVE, KEYS_IN_LAST_OCTAVE,
    KEY_PATTERN)


class GridCanvas(CustomCanvas):

    CANVAS_WIDTH = 480
    CANVAS_HEIGHT = 384
    MIN_CELL_WIDTH = 14

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
    COLOR_LINE_BAR = "#808080"
    COLOR_LINE_END = "#0000FF"
    COLOR_NOTE_OUTLINE_NORMAL = "#000000"
    COLOR_NOTE_OUTLINE_SEL = "#FF0000"
    COLOR_NOTE_FILL_NORMAL = "#FF0000"
    COLOR_NOTE_FILL_SEL = "#990000"
    COLOR_SHARP_ROW = "#F1F3F3"

    def __init__(self, parent, gstate, callbacks={}, **kwargs):
        CustomCanvas.__init__(self, parent, **kwargs)
        self.parent = parent

        self._init_data(gstate, callbacks)
        self._init_ui()
        self._bind_event_handlers()

        self.xview_moveto(0)
        self.yview_moveto(0)

    def _init_ui(self):
        cursor_img_path = "@{} black".format(CURSOR_SEL_IMG_PATH)

        self.config(
            width=GridCanvas.CANVAS_WIDTH,
            height=GridCanvas.CANVAS_HEIGHT,
            bg='white', cursor=cursor_img_path)

    def _init_data(self, gstate, callbacks):
        self._gstate = gstate
        self._callbacks = callbacks
        self._tool = GridCanvas.TOOL_SEL

        self.note_list = NoteList()
        self._notes_on_click = NoteList()
        self._mouse_state = MouseState()
        self._selection_bounds = None

        vs_height = int(self.config()['height'][4])
        vs_width = int(self.config()['width'][4])
        sr_width = self._gstate.width()
        sr_height = self._gstate.height() + 1
        self._visibleregion = [0, 0, vs_width, vs_height]
        scrollregion = (0, 0, sr_width, sr_height)
        self.config(scrollregion=scrollregion)

    def _bind_event_handlers(self):
        self.bind('<Configure>', self._on_window_resize)
        self.bind('<Motion>', self._on_mouse_motion)
        self.bind('<B1-Motion>', self._on_mouse_motion)
        self.bind('<ButtonPress-1>', self._on_bttnone_press)
        self.bind('<ButtonRelease-1>', self._on_bttnone_release)
        self.bind('<Control-a>', self._on_ctrl_a)
        self.bind('<Delete>', self._on_delete)

    def _draw_all(self):
        self._draw_horizontal_lines()
        self._draw_vertical_lines()
        self._draw_sharp_rows()

        visible_notes = filter(
            lambda note: self._is_note_visible(note),
            self.note_list.notes)
        self._update_note_ids(self._draw_notes(*visible_notes))

    def _draw_horizontal_lines(self):
        cell_height = self._gstate.cell_height()
        visibleregion_height = self._visibleregion[3]
        grid_height = self._gstate.height() + 1
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
        grid_height = self._gstate.height() + 1
        bar_width = self._gstate.bar_width()
        min_cell_width =self._gstate.min_cell_width(
            GridCanvas.MIN_CELL_WIDTH)
        cell_width = max(min_cell_width, self._gstate.cell_width())
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

        self.add_to_layer(
            GridCanvas.LAYER_VL, self.create_line,
            (grid_width, y1, grid_width, y2),
            fill=GridCanvas.COLOR_LINE_END,
            tags=('line', 'vertical'))

    def _draw_sharp_rows(self):
        pattern = KEY_PATTERN[::-1]
        grid_width = self._gstate.width()
        cell_height = self._gstate.cell_height()

        x1 = 0
        x2 = grid_width
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

            outline_color = (GridCanvas.COLOR_NOTE_OUTLINE_SEL if
                note.selected else GridCanvas.COLOR_NOTE_OUTLINE_NORMAL)
            fill_color = (GridCanvas.COLOR_NOTE_FILL_SEL if
                note.selected else GridCanvas.COLOR_NOTE_FILL_NORMAL)

            new_id = self.add_to_layer(
                GridCanvas.LAYER_RECT, self.create_rectangle,
                coords, outline=outline_color,
                fill=fill_color, tags='note')

            old_ids.append(note.id)
            new_ids.append(new_id)

        return zip(old_ids, new_ids)

    def _draw_selection_region(self, mousex, mousey):
        x1 = self._mouse_state.x
        y1 = self._mouse_state.y
        x2 = self.canvasx(mousex)
        y2 = self.canvasy(mousey)

        coords = (x1, y1, x2, y2)
        self.add_to_layer(GridCanvas.LAYER_SEL_REGION,
            self.create_rectangle, coords, fill='blue', outline='blue',
          stipple='gray12', tags='selection_region')

    def _update_mouse_state(self, event):
        self._mouse_state.x = self.canvasx(event.x)
        self._mouse_state.y = self.canvasy(event.y)
        self._mouse_state.item = self._rect_at(event)

        if not self._mouse_state.item:
            self._mouse_state.click = MouseState.EMPTY_AREA
        elif self._mouse_state.item not in self.note_list.selected_ids():
            self._mouse_state.click = MouseState.UNSELECTED_NOTE
        else:
            self._mouse_state.click = MouseState.SELECTED_NOTE

    def _update_scrollregion(self):
        scrollregion_width = max(
            self._gstate.width(), self._visibleregion[2])
        scrollregion_height = max(
            self._gstate.height() + 1, self._visibleregion[3])

        scrollregion = (0, 0, scrollregion_width,
            scrollregion_height)
        self.config(scrollregion=scrollregion)

    def _update_visibleregion(self):
        vr_left = self.canvasx(0)
        vr_top = self.canvasy(0)
        vr_width = self.winfo_width()
        vr_height = self.winfo_height()
        self._visibleregion = (vr_left, vr_top,
            vr_width, vr_height)

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
        rightmost = sorted(selected_rects,
            key=lambda r: r.right, reverse=True)[0]
        bottommost = sorted(selected_rects,
            key=lambda r: r.bottom, reverse=True)[0]

        left = leftmost.left
        top = topmost.top
        right = rightmost.right
        bottom = bottommost.bottom

        return (left, top, right, bottom)

    def _drag_notes(self, event):
        grid_height = self._gstate.height(zoom=False)
        cell_width = self._gstate.cell_width(zoom=False)
        cell_height = self._gstate.cell_height(zoom=False)
        cell_width_z = self._gstate.cell_width()
        cell_height_z = self._gstate.cell_height()

        eventx = self.canvasx(event.x)
        eventy = self.canvasy(event.y)
        mousex = self._mouse_state.x
        mousey = self._mouse_state.y

        dx = cell_width * round(float(eventx - mousex) / cell_width_z)
        dy = cell_height * round(float(eventy - mousey) / cell_height_z)

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
                before_rect.top - dy) / cell_height) - 1

    def _rect_at(self, event):
        mousex = event.x
        mousey = event.y
        ids = self.find_withtags('note')

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
        self._draw_all()

    def _on_mouse_motion(self, event):
        button1_state = event.state & 0x0100 == 0x0100
        if button1_state and self._tool == GridCanvas.TOOL_SEL:
            if self._mouse_state.click == MouseState.EMPTY_AREA:
                self.delete(*self.find_withtags('selection_region'))
                self._draw_selection_region(event.x, event.y)
            else:
                notes_selected = len(self.note_list.selected())
                if notes_selected:
                    self._drag_notes(event)
                    self._update_note_ids(self._draw_notes(
                        *self.note_list.selected()))

        if 'mousepos' in self._callbacks:
            x = self.canvasx(event.x)
            y = self.canvasy(event.y)
            self._callbacks['mousepos'](x, y)

    def _on_bttnone_press(self, event):
        self._update_mouse_state(event)

        if self._tool == GridCanvas.TOOL_SEL:
            self._do_sel(event)
        elif self._tool == GridCanvas.TOOL_PEN:
            self._do_pen(event)
        elif self._tool == GridCanvas.TOOL_ERASER:
            self._do_eraser(event)

        self._notes_on_click = self.note_list.copy_selected()
        self._selection_bounds = self._calc_selection_bounds()

    def _on_bttnone_release(self, event):
        mouse_x, mouse_y = self._mouse_state.x, self._mouse_state.y
        notes_selected = len(self.note_list.selected())
        dragged = mouse_x - event.x != 0 or mouse_y - event.y != 0

        if (notes_selected > 1 and self._mouse_state.click ==
            MouseState.SELECTED_NOTE and not dragged):
            self.deselect_note(GridCanvas.SEL)
            self.select_note(self._rect_at(event))

        selregion_id = self.find_withtags('selection_region')
        if (selregion_id and self._mouse_state.click ==
            MouseState.EMPTY_AREA and self._tool ==
            GridCanvas.TOOL_SEL and dragged):
            sel_region_id = self.find_withtags('selection_region')[0]
            coords = self.coords(sel_region_id)
            overlapping = self.find_overlapping(*coords)
            rects = self.find_withtags('note')
            overlapping_rects = set(overlapping).intersection(rects)
            self.select_note(*overlapping_rects)
            self._notes_on_click = self.note_list.copy_selected()
            self.delete(sel_region_id)

    def _on_ctrl_a(self, event):
        self.select_note(GridCanvas.ALL)

    def _on_delete(self, event):
        self.remove_note(GridCanvas.SEL)

    def _do_sel(self, event):
        ctrl_mask = 0x0004
        ctrl_pressed = (event.state & ctrl_mask == ctrl_mask)

        if ctrl_pressed:
            if self._mouse_state.click != MouseState.EMPTY_AREA:
                self.select_note(self._mouse_state.item)
                self._notes_on_click = self.note_list.copy_selected()
                self._selection_bounds = self._calc_selection_bounds()
        else:
            if self._mouse_state.click == MouseState.EMPTY_AREA:
                self.deselect_note(GridCanvas.SEL)
            elif self._mouse_state.click == MouseState.UNSELECTED_NOTE:
                self.deselect_note(GridCanvas.SEL)
                self.select_note(self._mouse_state.item)

    def _do_pen(self, event):
        grid_height = self._gstate.height(zoom=False)
        cell_width = self._gstate.cell_width(zoom=False)
        cell_height = self._gstate.cell_height(zoom=False)
        cell_width_z = self._gstate.cell_width()
        cell_height_z = self._gstate.cell_height()

        self.deselect_note(GridCanvas.ALL)

        canvasx = self.canvasx(event.x)
        canvasy = self.canvasy(event.y)

        if self._gstate.contains(canvasx, canvasy):
            x = cell_width * int(canvasx / cell_width_z)
            y = cell_height * int(canvasy / cell_height_z)

            midinumber = int((grid_height - y) / cell_height) - 1
            velocity = 100
            onset =  px_to_tick(x)
            dur = px_to_tick(cell_width)
            note = Note(midinumber, velocity, onset, dur, selected=True)
            self.add_note(note)

    def _do_eraser(self, event):
        self.deselect_note(GridCanvas.SEL)
        if self._mouse_state.item:
            self.remove_note(self._mouse_state.item)

    def on_update(self, new_gstate):
        diff = self._gstate - new_gstate
        self._gstate = new_gstate

        if 'subdiv' in diff:
            self.delete(*self.find_withtags('line', 'vertical'))
            self._draw_horizontal_lines()
            self._draw_vertical_lines()
        if any(x in diff for x in ['zoomx', 'zoomy']):
            self._update_scrollregion()
            self._update_visibleregion()
            self.delete(ALL)
            self._draw_all()
        if any(x in diff for x in ['beat_count', 'beat_unit', 'length']):
            self._update_scrollregion()
            self.delete(*self.find_withtags('line'))
            self.delete(*self.find_withtags('sharp_row'))
            self._draw_horizontal_lines()
            self._draw_vertical_lines()
            self._draw_sharp_rows()

    def get_note_list(self):
        return self.note_list.copy()

    def set_tool(self, value):
        self._tool = value

        paths = {
            0: CURSOR_SEL_IMG_PATH,
            1: CURSOR_PEN_IMG_PATH,
            2: CURSOR_ERASER_IMG_PATH
        }
        cursor_img_path = "@{} black".format(paths[value])
        self.config(cursor=cursor_img_path)

    def add_note(self, note):
        note.id = self._draw_notes(note)[0][1]
        self.note_list.add(note)
        self._notes_on_click.add(note)

        if 'dirty' in self._callbacks:
            self._callbacks['dirty'](self.note_list.copy())

    def remove_note(self, *args):
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

        if 'dirty' in self._callbacks:
            self._callbacks['dirty'](self.note_list.copy())

    def select_note(self, *args):
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
            self.itemconfig(note.id, fill=GridCanvas.COLOR_NOTE_FILL_SEL,
                            outline=GridCanvas.COLOR_NOTE_OUTLINE_SEL)
            note.selected = True

    def deselect_note(self, *args):
        argc = len(args)
        if argc == 0:
            return
        if (argc == 1 and args[0] in
            [GridCanvas.SEL, GridCanvas.ALL, 'all', 'sel']):
            notes = self.note_list.selected()
        else:
            notes = (self.note_list.from_id(id) for id in args)

        for note in notes:
            self.itemconfig(note.id, fill=GridCanvas.COLOR_NOTE_FILL_NORMAL,
                            outline=GridCanvas.COLOR_NOTE_OUTLINE_NORMAL)
            note.selected = False

    def xview(self, *args):
        self.delete(*self.find_withtags('line'))
        self.delete(*self.find_withtags('note'))
        CustomCanvas.xview(self, *args)
        self._update_visibleregion()

        self._draw_horizontal_lines()
        self._draw_vertical_lines()
        visible_notes = filter(
            lambda note: self._is_note_visible(note),
            self.note_list.notes)
        self._update_note_ids(self._draw_notes(*visible_notes))

    def yview(self, *args):
        self.delete(*self.find_withtags('line'))
        self.delete(*self.find_withtags('note'))
        CustomCanvas.yview(self, *args)
        self._update_visibleregion()

        self._draw_horizontal_lines()
        self._draw_vertical_lines()
        visible_notes = filter(
            lambda note: self._is_note_visible(note),
            self.note_list.notes)
        self._update_note_ids(self._draw_notes(*visible_notes))