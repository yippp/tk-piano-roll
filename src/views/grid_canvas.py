from Tkinter import *
from include.custom_canvas import CustomCanvas
from src.observables.piano_roll_observable import PianoRollObservable
from src.observables.grid_observable import GridObservable
from src.observables.note_list_observable import NoteListObservable
from src.models.note_list_model import NoteListModel
from src.models.note_model import NoteModel
from src.rect import Rect
from src.helper import (get_image_path, velocity_to_color,
    px_to_tick, tick_to_px)
from src.const import (
    KEYS_IN_OCTAVE, KEYS_IN_LAST_OCTAVE,
    KEY_PATTERN)


NOTE_SEL = -1
NOTE_ALL = -2


class GridCanvas(CustomCanvas):

    class Click(object):

        EMPTY_AREA = 0
        UNSELECTED_NOTE = 1
        SELECTED_NOTE = 2

        def __init__(self, x=0, y=0, ctrl=False):
            self.x = x
            self.y = y
            self.ctrl = ctrl
            self.item = None
            self.where = GridCanvas.Click.EMPTY_AREA

    CANVAS_WIDTH = 480
    CANVAS_HEIGHT = 384
    MIN_CELL_WIDTH = 14

    TOOL_SEL = 0
    TOOL_PEN = 1
    TOOL_ERASER = 2

    COLOR_LINE_NORMAL = "#CCCCCC"
    COLOR_LINE_BAR = "#000000"
    COLOR_LINE_END = "#FF0000"
    COLOR_LINE_PLAY = "#00BFFF"
    COLOR_NOTE_OUTLINE = "#000000"
    COLOR_NOTE_FILL = "#0080FF"
    COLOR_SHARP_ROW = "#F1F3F3"

    def __init__(self, parent, callbacks=None, **kwargs):
        CustomCanvas.__init__(self, parent, **kwargs)
        self.parent = parent

        self._init_data(callbacks)
        self._init_ui()
        self._bind_event_handlers()

    def _init_data(self, callbacks):
        self._callbacks = callbacks

        self._click = GridCanvas.Click()
        self._tool = GridCanvas.TOOL_SEL
        self._selection_bounds = None
        self._ntflag = True

        self._piano_roll_observable = PianoRollObservable()
        self._grid = GridObservable()
        self._note_list = NoteListObservable()
        self._selection = NoteListObservable()
        self._clipboard = NoteListObservable()

        self._grid.register_observer(
            self._on_grid_state_change)
        self._note_list.register_observer(
            self._on_note_state_change)
        self._selection.register_observer(
            self._on_selection_state_change)
        self._clipboard.register_observer(
            self._on_clipboard_state_change)

    def _init_ui(self):
        self.config(
            width=GridCanvas.CANVAS_WIDTH,
            height=GridCanvas.CANVAS_HEIGHT,
            bg='white')

        if sys.platform in ['linux', 'linux2']:
            cursor_spec = "@{} black".format(
                get_image_path('cursor_sel.xbm'))
            self.config(cursor=cursor_spec)

    def _bind_event_handlers(self):
        self.bind('<Configure>', self._on_window_resize)
        self.bind('<Motion>', self._on_mouse_motion)
        self.bind('<B1-Motion>', self._on_mouse_motion)
        self.bind('<ButtonPress-1>', self._on_bttnone_press)
        self.bind('<ButtonRelease-1>', self._on_bttnone_release)
        self.bind('<Double-Button-1>', self._on_bttnone_double)

    def _on_window_resize(self, event):
        self._update_scrollregion()
        self._update_visibleregion()
        self._draw_all()

    def _on_mouse_motion(self, event):
        button1_pressed = event.state & 0x0100 == 0x0100
        if button1_pressed and self._tool == GridCanvas.TOOL_SEL:
            if self._click.where == GridCanvas.Click.EMPTY_AREA:
                self.delete(*self.find_withtags('selection_region'))
                self._draw_selection_region(event.x, event.y)
            elif self._selection.state:
                self._update_note_pos(event)

                old_ids, new_ids = self._draw_notes(
                    *self._selection.state)
                self._update_note_ids(zip(old_ids, new_ids))
                self.delete(*old_ids)
                self._selection_bounds = self._calc_selection_bounds()

        grid_state = self._grid.state
        grid_width = grid_state.width()
        grid_height = grid_state.height()
        grid_rect = Rect.at_origin(grid_width, grid_height)
        if grid_rect.collide_point(event.x, event.y):
            x = self.canvasx(event.x)
            y = self.canvasy(event.y)
            self._callbacks['mouse_pos'](x, y)

    def _on_bttnone_press(self, event):
        self._update_mouse_state(event)

        if self._tool == GridCanvas.TOOL_SEL:
            self._do_sel(event)
        elif self._tool == GridCanvas.TOOL_PEN:
            self._do_pen(event)
        elif self._tool == GridCanvas.TOOL_ERASER:
            self._do_eraser(event)

        self._selection_bounds = self._calc_selection_bounds()

    def _on_bttnone_release(self, event):
        mouse_x, mouse_y = self._click.x, self._click.y
        dragged = mouse_x - event.x != 0 or mouse_y - event.y != 0

        if (self._click.where == GridCanvas.Click.SELECTED_NOTE and
            len(self._selection.state) > 1 and not dragged):
            self.select_notes(self._note_at(event))

        selregion_id = self.find_withtags('selection_region')
        if (self._click.where == GridCanvas.Click.EMPTY_AREA and
            selregion_id and self._tool == GridCanvas.TOOL_SEL and
            dragged):
            sel_region_id = self.find_withtags('selection_region')[0]
            coords = self.coords(sel_region_id)
            overlapping = self.find_overlapping(*coords)
            notes = self.find_withtags('note')
            overlapping_notes = set(overlapping).intersection(notes)

            self.select_notes(*overlapping_notes)
            self.delete(sel_region_id)

        selected_ids = self._selection.state.ids
        selected = NoteListModel(
            [self._note_list.state.get(id) for
            id in selected_ids])
        if selected != self._selection.state:
            self.disable_notifications()
            self._note_list.remove(*self._selection.state.ids)
            self._note_list.add(*self._selection.state.copy())
            self.enable_notifications()

    def _on_bttnone_double(self, event):
        if self._tool == GridCanvas.TOOL_SEL:
            grid_state = self._grid.state
            cell_width = grid_state.cell_width()
            zoomx = grid_state.zoom[0]
            x = (int(self.canvasx(float(event.x)) /
                cell_width) * cell_width)
            self.set_cursor(px_to_tick(x / zoomx))

    def _on_grid_state_change(self, grid_state):
        self._piano_roll_observable.set_grid(grid_state)

    def _on_note_state_change(self, note_state):
        self._piano_roll_observable.set_notes(note_state)

    def _on_selection_state_change(self, selection_state):
        self._piano_roll_observable.set_selection(
            selection_state)

    def _on_clipboard_state_change(self, clipboard_state):
        self._piano_roll_observable.set_clipboard(
            clipboard_state)

    def _draw_all(self):
        self.delete(ALL)
        self._draw_horizontal_lines()
        self._draw_vertical_lines()
        self._draw_end_line()
        self._draw_cursor_line()
        self._draw_sharp_rows()

        visible = filter(
            lambda id: self._is_note_visible(id),
            self._note_list.state.ids)
        old_ids, new_ids = self._draw_notes(*visible)
        self.delete(*old_ids)
        self._update_note_ids(zip(old_ids, new_ids))

    def _draw_horizontal_lines(self):
        vr_left, vr_top, vr_width, vr_height = self._visibleregion
        grid_state = self._grid.state
        grid_width = grid_state.width()

        x1 = self.canvasx(0)
        x2 = self.canvasx(x1 + min(grid_width, vr_width))

        for i, y in enumerate(
            grid_state.ycoords(vr_top, vr_top + vr_height)):
            if (i + 4) % 12:
                fill = GridCanvas.COLOR_LINE_NORMAL
                layer = 5
            else:
                fill = GridCanvas.COLOR_LINE_BAR
                layer = 3

            coords = (x1, y, x2, y)
            self.add_to_layer(
                layer, self.create_line, coords, fill=fill,
                tags=('line', 'horizontal', 'grid'))

    def _draw_vertical_lines(self):
        vr_left, vr_top, vr_width, vr_height = self._visibleregion
        grid_state = self._grid.state
        grid_height = grid_state.height() + 1
        bar_width = grid_state.bar_width()
        cur_subdiv = grid_state.subdiv
        min_subdiv = grid_state.min_subdiv(15)

        y1 = vr_top
        y2 = self.canvasy(y1 + min(vr_height, grid_height))

        for x in grid_state.xcoords(
            vr_left, vr_left + vr_width,
            subdiv=min(cur_subdiv, min_subdiv)):
            if x % bar_width:
                color = GridCanvas.COLOR_LINE_NORMAL
            else:
                color = GridCanvas.COLOR_LINE_BAR

            coords = (x, y1, x, y2)
            self.add_to_layer(
                4, self.create_line, coords, fill=color,
                tags=('line', 'vertical', 'grid'))

    def _draw_end_line(self):
        vr_left, vr_top, vr_width, vr_height = self._visibleregion
        grid_state = self._grid.state
        grid_width = grid_state.width()
        grid_height = grid_state.height()
        y1 = vr_top
        y2 = self.canvasy(y1 + min(vr_height, grid_height))
        coords = (grid_width, y1, grid_width, y2)

        self.add_to_layer(
            2, self.create_line, coords,
            fill=GridCanvas.COLOR_LINE_END,
            tags=('line', 'vertical', 'end'))

    def _draw_cursor_line(self):
        vr_left, vr_top, vr_width, vr_height = self._visibleregion

        grid_height = self._grid.state.height()
        zoomx =  self._grid.state.zoom[0]
        cursor = self._piano_roll_observable.state.cursor
        x = tick_to_px(cursor) * zoomx
        y1 = vr_top
        y2 = self.canvasy(y1 + min(vr_height, grid_height))
        coords = (x, y1, x, y2)

        self.add_to_layer(
            1, self.create_line, coords,
            fill=GridCanvas.COLOR_LINE_PLAY,
            tags=('line', 'vertical', 'cursor'))

    def _draw_sharp_rows(self):
        vr_width = self._visibleregion[2]
        grid_width = self._grid.state.width()
        cell_height = self._grid.state.cell_height()

        pattern = KEY_PATTERN[::-1]

        x1 = self.canvasx(0)
        x2 = self.canvasx(x1 + min(grid_width, vr_width))

        for i, y in enumerate(self._grid.state.ycoords()):
            i = (i + KEYS_IN_OCTAVE - KEYS_IN_LAST_OCTAVE) % 12
            key = pattern[i]
            if key == '1': continue

            coords = (x1, y, x2, y + cell_height)
            self.add_to_layer(
                6, self.create_rectangle, coords,
                fill=GridCanvas.COLOR_SHARP_ROW,
                width=0, tags='sharp_row')

    def _draw_notes(self, *args):
        old_ids = []
        new_ids = []

        for arg in args:
            if isinstance(arg, (int, long)):
                note = self._note_list.state.get(arg)
            else:
                note = arg

            rect = note.rect
            x1 = rect.left * self._grid.state.zoom[0]
            y1 = rect.top * self._grid.state.zoom[1]
            x2 = x1 + rect.width * self._grid.state.zoom[0]
            y2 = y1 + rect.height * self._grid.state.zoom[1]
            coords = (x1, y1, x2, y2)

            outline_color = GridCanvas.COLOR_NOTE_OUTLINE
            fill_color = velocity_to_color(
                note.velocity, GridCanvas.COLOR_NOTE_FILL,
                0.7 if note.id in self._selection.state.ids
                else 1)

            new_id = self.add_to_layer(
                2, self.create_rectangle, coords,
                outline=outline_color, fill=fill_color,
                width=1, tags='note')

            old_ids.append(note.id)
            new_ids.append(new_id)

        return old_ids, new_ids

    def _draw_selection_region(self, mousex, mousey):
        x1 = self._click.x
        y1 = self._click.y
        x2 = self.canvasx(mousex)
        y2 = self.canvasy(mousey)

        coords = (x1, y1, x2, y2)
        self.add_to_layer(
            0, self.create_rectangle, coords, fill='blue',
            outline='blue', stipple='gray12',
            tags='selection_region')

    def _update_note_pos(self, event):
        grid_width = self._grid.state.width(zoomed=False)
        grid_height = self._grid.state.height(zoomed=False)
        grid_rect = Rect.at_origin(grid_width, grid_height)

        cell_width = self._grid.state.cell_width(zoomed=False)
        cell_height = self._grid.state.cell_height(zoomed=False)
        zoom_x, zoom_y = self._grid.state.zoom

        drag_x = self.canvasx(event.x)
        drag_y = self.canvasy(event.y)
        drag_col = int(drag_x / cell_width / zoom_x)
        drag_row = int(drag_y / cell_height / zoom_y)

        anchor = self._selection.state.get(
            self._click.item)
        anchor_x = anchor.rect.left
        anchor_y = anchor.rect.top
        anchor_col = int(anchor_x / cell_width)
        anchor_row = int(anchor_y / cell_height)

        col_dist = drag_col - anchor_col
        row_dist = drag_row - anchor_row
        dx = col_dist * cell_width
        dy = row_dist * cell_height

        d_onset = (px_to_tick(dx) if grid_rect.contains_rect(
            self._selection_bounds.move(dx, 0)) else 0)
        d_midinumber = (-row_dist if grid_rect.contains_rect(
            self._selection_bounds.move(0, dy)) else 0)

        self._selection.change(
            d_midinumber, 0, d_onset, 0,
            *self._selection.state.ids)

    def _update_note_ids(self, ids):
        for old_id, new_id in ids:
            self._note_list.state.get(old_id).id = new_id
            if self._selection.state.get(old_id):
                self._selection.state.get(old_id).id = new_id
            if self._click.item == old_id:
                self._click.item = new_id

    def _update_mouse_state(self, event):
        self._click.x = self.canvasx(event.x)
        self._click.y = self.canvasy(event.y)
        self._click.item = self._note_at(event)

        if not self._click.item:
            self._click.where = GridCanvas.Click.EMPTY_AREA
        elif self._click.item not in self._selection.state.ids:
            self._click.where = GridCanvas.Click.UNSELECTED_NOTE
        else:
            self._click.where = GridCanvas.Click.SELECTED_NOTE

    def _update_scrollregion(self):
        grid_width = self._grid.state.width()
        grid_height = self._grid.state.height()
        sr_width = max(grid_width, self.winfo_width())
        sr_height = max(grid_height + 1, self.winfo_height())
        scrollregion = (0, 0, sr_width, sr_height)
        self.config(scrollregion=scrollregion)

    def _update_visibleregion(self):
        vr_left = self.canvasx(0)
        vr_top = self.canvasy(0)
        vr_width = self.winfo_width()
        vr_height = self.winfo_height()
        self._visibleregion = (vr_left, vr_top,
            vr_width, vr_height)

    def _is_note_visible(self, id):
        note = self._note_list.state.get(id)
        visibleregion_rect = Rect(*self._visibleregion)
        grid_state = self._grid.state
        note_rect = note.rect.xscale(
            grid_state.zoom[0]).yscale(
            grid_state.zoom[1])
        return visibleregion_rect.collide_rect(note_rect)

    def _calc_selection_bounds(self):
        if not self._selection.state:
            return None

        selected_rects = [note.rect for note in self._selection.state]
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

        return Rect(left, top, right - left, bottom - top)

    def _note_at(self, event):
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

    def _do_sel(self, event):
        ctrl_mask = 0x0004
        ctrl_pressed = (event.state & ctrl_mask == ctrl_mask)

        if ctrl_pressed:
            if self._click.where != GridCanvas.Click.EMPTY_AREA:
                self.select_notes(self._click.item)
        else:
            if self._click.where == GridCanvas.Click.EMPTY_AREA:
                self.deselect_notes(NOTE_ALL)
            elif self._click.where == GridCanvas.Click.UNSELECTED_NOTE:
                self._note_list.disable_notifications()
                self.deselect_notes(NOTE_ALL)
                self.select_notes(self._click.item)
                self._note_list.enable_notifications()

    def _do_pen(self, event):
        grid_height = self._grid.state.height(zoomed=False)
        cell_width = self._grid.state.cell_width(zoomed=False)
        cell_height = self._grid.state.cell_height(zoomed=False)
        cell_width_z = self._grid.state.cell_width()
        cell_height_z = self._grid.state.cell_height()

        canvasx = self.canvasx(event.x)
        canvasy = self.canvasy(event.y)

        if self._grid.state.contains(canvasx, canvasy):
            self.disable_notifications()

            x = cell_width * int(canvasx / cell_width_z)
            y = cell_height * int(canvasy / cell_height_z)

            midinumber = int((grid_height - y) / cell_height) - 1
            velocity = 100
            onset =  px_to_tick(x)
            dur = px_to_tick(cell_width)
            id = self.add_notes((
                midinumber, velocity, onset, dur))[0]
            self.deselect_notes(NOTE_ALL)
            self.select_notes(id)

            self.enable_notifications()

    def _do_eraser(self, event):
        self.select_notes(None)
        if self._click.item:
            self.remove_notes(self._click.item)

    def _get_ids(self, *args):
        argc = len(args)
        if argc == 0 or (argc == 1 and not args[0]):
            return []
        elif argc == 1 and args[0] in [NOTE_SEL, 'sel']:
            return self._selection.state.ids
        elif argc == 1 and args[0] in [NOTE_ALL, 'all']:
            note_state = self._note_list.state
            return [note.id for note in note_state]
        else:
            return args

    def add_notes(self, *args):
        if not args:
            return

        notes = []
        ids = []
        for arg in args:
            if isinstance(arg, (tuple, list)):
                note = NoteModel(*arg)
            elif isinstance(arg, NoteModel):
                note = arg
            else:
                raise ValueError

            note.id = self._draw_notes(note)[1][0]
            notes.append(note)
            ids.append(note.id)

        self._note_list.add(*notes)
        return ids

    def edit_notes(self, attr, value, *args):
        ids = self._get_ids(*args)

        if not ids:
            return

        sel_ids = [id for id in ids if
            id in self._selection.state.ids]
        self._note_list.set(attr, value, *ids)
        self._selection.set(attr, value, *sel_ids)
        old_ids, new_ids = self._draw_notes(*ids)
        self.delete(*old_ids)
        self._update_note_ids(zip(old_ids, new_ids))

    def remove_notes(self, *args):
        if not args:
            return

        ids = self._get_ids(*args)
        for id in ids: self.delete(id)
        self._note_list.remove(*ids)

        selected_ids = [id for id in ids if
            id in self._selection.state.ids]
        self._selection.remove(*selected_ids)

    def select_notes(self, *args):
        ids = self._get_ids(*args)
        existing_ids = [id for id in ids if
            id not in self._selection.state.ids]

        to_select = []
        for i, id in enumerate(existing_ids):
            note = self._note_list.state.get(id)
            fill_color = velocity_to_color(
                note.velocity,
                GridCanvas.COLOR_NOTE_FILL,
                0.7)
            self.itemconfig(note.id, fill=fill_color)
            to_select.append(note.copy())

        self._selection.add(*to_select)

    def deselect_notes(self, *args):
        ids = self._get_ids(*args)
        existing_ids = [id for id in ids if
            id in self._selection.state.ids]

        to_deselect = []
        for i, id in enumerate(existing_ids):
            note = self._note_list.state.get(id)
            fill_color = velocity_to_color(
                note.velocity,
                GridCanvas.COLOR_NOTE_FILL,
                1)
            self.itemconfig(note.id, fill=fill_color)
            to_deselect.append(id)

        self._selection.remove(*to_deselect)

    def copy_notes(self, move_cursor, *args):
        ids = self._get_ids(*args)

        self.disable_notifications()
        self._clipboard.remove(*self._clipboard.state.ids)
        self._clipboard.add(
            *[self._note_list.state.get(id) for id in ids])
        self.enable_notifications()

        if move_cursor:
            last_note = self._clipboard.state[-1]
            self.set_cursor(
                last_note.onset + last_note.duration)

    def paste_notes(self):
        notes = []
        cursor = self._piano_roll_observable.state.cursor
        first = self._clipboard.state[0]
        for note in self._clipboard.state:
            new_note = note.copy()
            new_note.onset = (note.onset -
                first.onset + cursor)
            notes.append(new_note)

        to_paste = NoteListModel(notes)
        last_note = to_paste[-1]
        self.set_cursor(
            last_note.onset + last_note.duration)

        self.add_notes(*[note for note in to_paste])
        self.deselect_notes(NOTE_ALL)
        self.select_notes(*to_paste.ids)

    def set_subdiv(self, subdiv):
        self._grid.set_subdiv(subdiv)
        self.delete(*self.find_withtags('line', 'vertical', 'grid'))
        self._draw_vertical_lines()

    def set_zoom(self, zoom):
        self._grid.set_zoom(zoom)
        self._update_scrollregion()
        self._update_visibleregion()
        self._draw_all()

    def set_timesig(self, timesig):
        self._grid.set_timesig(timesig)

        self.delete(*self.find_withtags('line'))
        self.delete(*self.find_withtags('sharp_row'))
        self._update_scrollregion()
        self._update_visibleregion()
        self._draw_horizontal_lines()
        self._draw_vertical_lines()
        self._draw_end_line()
        self._draw_cursor_line()
        self._draw_sharp_rows()

    def set_end(self, end):
        self._grid.set_end(end)

        self.delete(*self.find_withtags('line'))
        self.delete(*self.find_withtags('sharp_row'))
        self._update_scrollregion()
        self._update_visibleregion()
        self._draw_horizontal_lines()
        self._draw_vertical_lines()
        self._draw_end_line()
        self._draw_cursor_line()
        self._draw_sharp_rows()

    def set_cursor(self, ticks):
        self._piano_roll_observable.set_cursor(ticks)
        self.delete(*self.find_withtags('line', 'cursor'))
        self._draw_cursor_line()

    def set_tool(self, value):
        self._tool = value
        if sys.platform in ['linux', 'linux2']:
            paths = {
                0: get_image_path('cursor_sel.xbm'),
                1: get_image_path('cursor_pen.xbm'),
                2: get_image_path('cursor_eraser.xbm')
            }
            cursor_img_path = "@{} black".format(paths[value])
            self.config(cursor=cursor_img_path)

    def enable_notifications(self):
        self._piano_roll_observable.enable_notifications()

    def disable_notifications(self):
        self._piano_roll_observable.disable_notifications()

    def register_observer(self, observer, tag):
        self._piano_roll_observable.register_observer(
            observer, tag)

    def unregister_observer(self, observer):
        self._piano_roll_observable.unregister_observer(
            observer)

    def xview(self, *args):
        CustomCanvas.xview(self, *args)
        self._update_visibleregion()
        self._draw_all()

    def yview(self, *args):
        CustomCanvas.yview(self, *args)
        self._update_visibleregion()
        self._draw_all()
