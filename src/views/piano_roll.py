import os
from Tkinter import *
from tkMessageBox import askyesnocancel
from tkFileDialog import askopenfilename
from src.observables.piano_roll_observable import (OBS_GRID,
    OBS_NOTE, OBS_SELECTION, OBS_CLIPBOARD)
from src.models.piano_roll_model import PianoRollModel
from piano_roll_menu import PianoRollMenu
from main_frame import MainFrame
from grid_canvas import NOTE_ALL, NOTE_SEL
from toolbar import Toolbar
from bottombar import BottomBar
from src.stack import Stack
from src.helper import (make_title,
    get_image_path, save_composition,
    load_composition, to_ticks)


class PianoRoll(Frame):

    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.parent = parent

        self._init_data()
        self._init_ui()

    def _init_data(self):
        self._states = Stack([PianoRollModel()], maxsize=100)
        self._last_saved_state = PianoRollModel()
        self._initial_dir = None
        self._filepath = None
        self._dirty = False

    def _init_ui(self):
        root = self._root()
        try:
            image_path = get_image_path('icon.gif')
            image = PhotoImage(file=image_path)
            root.tk.call('wm', 'iconphoto', root._w, image)
        except TclError:
            print "Couldn't load icon file"

        callbacks = self._make_callbacks()
        self._bind_global_commands(callbacks['global'])

        self.menu = PianoRollMenu(root, callbacks['global'])
        root.config(menu=self.menu)
        root.title(make_title("Untitled", self._dirty))

        self.main_frame = MainFrame(self)
        self.toolbar = Toolbar(self, callbacks['toolbar'])
        self.bottombar = BottomBar(self, callbacks['bottombar'])

        self.main_frame.grid_canvas.register_observer(
            self.on_grid_change, OBS_GRID)
        self.main_frame.grid_canvas.register_observer(
            self.on_note_change, OBS_NOTE)
        self.main_frame.grid_canvas.register_observer(
            self.on_selection_change, OBS_SELECTION)
        self.main_frame.grid_canvas.register_observer(
            self.on_clipboard_change, OBS_CLIPBOARD)

        self.toolbar.pack(side=TOP, fill=X)
        self.bottombar.pack(side=BOTTOM, fill=X)
        self.main_frame.pack(fill=BOTH, expand=True)
        self.pack(fill=BOTH, expand=True)

    def _bind_global_commands(self, commands):
        self.bind_all(
            "<Control-n>",
            lambda event: commands['new']())
        self.bind_all(
            "<Control-o>",
            lambda event: commands['open']())
        self.bind_all(
            "<Control-s>",
            lambda event: commands['save']())
        self.bind_all(
            "<Control-w>",
            lambda event: commands['exit']())
        self.bind_all(
            "<Control-x>",
            lambda event: commands['cut']())
        self.bind_all(
            "<Control-z>",
            lambda event: commands['undo']())
        self.bind_all(
            "<Control-y>",
            lambda event: commands['redo']())
        self.bind_all(
            "<Control-c>",
            lambda event: commands['copy']())
        self.bind_all(
            "<Control-v>",
            lambda event: commands['paste']())
        self.bind_all(
            "<Delete>",
            lambda event: commands['delete']())
        self.bind_all(
            "<Control-a>",
            lambda event: commands['select_all']())
        self.bind_all(
            "1",
            lambda event: commands['tool'](0))
        self.bind_all(
            "2",
            lambda event: commands['tool'](1))
        self.bind_all(
            "3",
            lambda event: commands['tool'](2))

    def _make_callbacks(self):
        def global_new():
            if self._dirty:
                title = "New Score"
                msg = ("Save changes before starting "
                    "new score?")
                answer = askyesnocancel(title, msg)

                if answer is None:
                    return
                elif answer:
                    if self._filepath:
                        global_save()
                    elif not global_save_as():
                        return

            self._states = Stack(
                [PianoRollModel()], maxsize=100)
            self.update_state(self._states.current)

            self._filepath = None
            self.set_dirty(False)

        def global_open():
            if self._dirty:
                title = "Open Score"
                msg = ("Save changes before opening a "
                    "new score?")
                answer = askyesnocancel(title, msg)

                if answer is None:
                    return
                elif answer:
                    if self._filepath:
                        global_save()
                    elif not global_save_as():
                        return False

            filename = askopenfilename(
                parent=self, initialdir=self._initial_dir)
            if not filename: return False

            self._initial_dir = os.path.dirname(filename)
            self._filepath = filename

            comp_state = load_composition(filename)
            self._states = Stack([comp_state], maxsize=100)
            self.update_state(self._states.current)
            self._last_saved_state = comp_state

            self.set_dirty(False)

        def global_save():
            if not self._filepath:
                global_save_as()
            else:
                self._save_cmd()

        def global_save_as():
            from tkFileDialog import asksaveasfilename

            initial_file = os.path.basename(
                self._filepath or "Untitled")
            filename = asksaveasfilename(
                parent=self, initialdir=self._initial_dir,
                initialfile=initial_file)
            if not filename:
                return False
            self._filepath = filename
            self._initial_dir = os.path.dirname(filename)

            self._save_cmd()

            return True

        def global_exit():
            if self._dirty:
                title = "Exit"
                msg = "Save changes before exiting?"
                answer = askyesnocancel(title, msg)

                if answer is None:
                    return
                elif answer:
                    if self._filepath:
                        global_save()
                    elif not global_save_as():
                        return False

            self.quit()

        def global_undo():
            if self._states.pointer < self._states.size:
                self._states.pointer = min(
                    self._states.pointer + 1,
                    self._states.size - 1)

                self.update_state(self._states.current)

                if self._states.pointer == self._states.size - 1:
                    self.menu.set_entry_state(0, DISABLED)

                if self._states.pointer > 0:
                    self.menu.set_entry_state(1, NORMAL)

        def global_redo():
            if self._states.pointer > 0:
                self._states.pointer = max(
                    self._states.pointer - 1, 0)

                self.update_state(self._states.current)

                if self._states.pointer < self._states.size:
                    self.menu.set_entry_state(0, NORMAL)

                if self._states.pointer == 0:
                    self.menu.set_entry_state(1, DISABLED)

        def global_cut():
            self.main_frame.grid_canvas.copy_notes(False, NOTE_SEL)
            self.main_frame.grid_canvas.remove_notes(NOTE_SEL)

        def global_copy():
            self.main_frame.grid_canvas.copy_notes(True, NOTE_SEL)

        def global_paste():
            self.main_frame.grid_canvas.paste_notes()

        def global_delete():
            self.main_frame.grid_canvas.remove_notes(NOTE_SEL)

        def global_clear():
            self.main_frame.grid_canvas.remove_notes(NOTE_ALL)

        def global_select_all():
            self.main_frame.grid_canvas.select_notes(NOTE_ALL)
            global_set_tool(0)

        def global_set_tool(value):
            self.toolbar.toolbox.set(value)
            self.main_frame.grid_canvas.set_tool(value)

        def toolbar_set_subdiv(subdiv):
            self.main_frame.grid_canvas.set_subdiv(subdiv)

        def toolbar_set_tool(tool):
            self.main_frame.grid_canvas.set_tool(tool)

        def toolbar_set_note(attr, value):
            self.main_frame.grid_canvas.edit_notes(
                attr, value, 'sel')

        def bottombar_set_end(end):
            self.main_frame.grid_canvas.set_end(end)

        def bottombar_set_timesig(timesig):
            self.main_frame.grid_canvas.set_timesig(timesig)

            beat_count, beat_unit = timesig
            self.bottombar.end_frame.set_max_beat(beat_count)

            ticks = to_ticks(0, 1, 0, beat_count, beat_unit) - 1
            self.bottombar.end_frame.set_max_tick(ticks)

        return {
            'global': {
                'new': global_new,
                'open': global_open,
                'save': global_save,
                'save_as': global_save_as,
                'exit': global_exit,
                'undo': global_undo,
                'redo': global_redo,
                'cut': global_cut,
                'copy': global_copy,
                'paste': global_paste,
                'delete': global_delete,
                'clear': global_clear,
                'select_all': global_select_all,
                'tool': global_set_tool
            },
            'toolbar': {
                'snap': toolbar_set_subdiv,
                'tool': toolbar_set_tool,
                'note': toolbar_set_note
            },
            'bottombar': {
                'end': bottombar_set_end,
                'timesig': bottombar_set_timesig
            }
        }

    def _save_cmd(self):
        assert self._filepath
        save_composition(self._filepath, self._states.current)
        self._last_saved_state = self._states.current
        self.set_dirty(False)

    def on_grid_change(self, new_grid):
        curr_grid = self._states.current.grid
        saved_grid = self._last_saved_state.grid

        if not curr_grid.compare(
            new_grid, 'timesig', 'end'):
            new_state = self._states.current.copy()
            new_state.grid = new_grid
            self._states.append(new_state)

        self.set_dirty(not saved_grid.compare(
            new_grid, 'timesig', 'end'))

        if self._states.current != self._states.bottom:
            self.menu.set_entry_state(0, NORMAL)

        if self._states.current == self._states.top:
            self.menu.set_entry_state(1, DISABLED)

    def on_note_change(self, new_notes):
        curr_notes = self._states.current.notes
        saved_notes = self._last_saved_state.notes

        if curr_notes != new_notes:
            new_state = self._states.current.copy()
            new_state.notes = new_notes
            self._states.append(new_state)

        self.set_dirty(saved_notes != new_notes)

        if self._states.current != self._states.bottom:
            self.menu.set_entry_state(0, NORMAL)

        if self._states.current == self._states.top:
            self.menu.set_entry_state(1, DISABLED)

    def on_selection_change(self, new_selection):
        if new_selection:
            menu_entries_state = NORMAL
            note_edit_frame_state = 'readonly'
            self.toolbar.note_data_frame.set_note(
                new_selection[0])
        else:
            menu_entries_state = DISABLED
            note_edit_frame_state = DISABLED

        for i in range(3, 7):
            self.menu.set_entry_state(i, menu_entries_state)
        self.toolbar.note_data_frame.set_state(
            note_edit_frame_state)

    def on_clipboard_change(self, new_clipboard):
        if new_clipboard:
            self.menu.set_entry_state(5, NORMAL)
        else:
            self.menu.set_entry_state(5, DISABLED)

    def set_dirty(self, dirty):
        self._dirty = dirty
        filename = self._filepath or "Untitled"
        self._root().title(
            make_title(os.path.basename(filename), dirty))

    def update_state(self, state):
        grid = state.grid
        notes = state.notes

        self.bottombar.timesig_frame.set_timesig(grid.timesig)
        self.bottombar.end_frame.set_end(grid.end, notify=False)

        self.main_frame.grid_canvas.disable_notifications()
        self.main_frame.grid_canvas.set_timesig(
            grid.timesig)
        self.main_frame.grid_canvas.set_end(
            grid.end)
        self.main_frame.grid_canvas.remove_notes(NOTE_ALL)
        self.main_frame.grid_canvas.add_notes(*notes.copy())
        self.main_frame.grid_canvas.enable_notifications()
