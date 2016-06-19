import os
from Tkinter import *
from tkMessageBox import askyesnocancel
from tkFileDialog import askopenfilename
from piano_roll_menu import PianoRollMenu
from piano_roll_frame import PianoRollFrame
from toolbar import Toolbar
from bottombar import BottomBar
from ..helper import (make_title,
    save_song, load_song)
from ..paths import ICON_IMG_PATH

class PianoRoll(Frame):

    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.parent = parent

        self._init_data()
        self._init_ui()

    def _init_data(self):
        self._initial_dir = None
        self._filepath = None
        self._dirty = False

    def _init_ui(self):
        menu_cb = {
            'new': self._new_cmd,
            'open': self._open_cmd,
            'save': self._save_cmd,
            'save_as': self._save_as_cmd,
            'exit': self._exit_cmd
        }

        toolbar_cb = {
            'snap': self.set_snap,
            'zoom': {
                'zoomx': self.set_zoomx,
                'zoomy': self.set_zoomy
            },
            'tool': self.set_canvas_tool
        }

        bottombar_cb = {
            'length': self.set_canvas_length,
            'timesig': self.set_canvas_timesig
        }

        root = self._root()
        menu = PianoRollMenu(root, menu_cb)
        root.config(menu=menu)
        root.title(make_title("Untitled", self._dirty))

        try:
            image = PhotoImage(file=ICON_IMG_PATH)
            root.tk.call('wm', 'iconphoto', root._w, image)
        except TclError:
            print "Couldn't load icon file"

        self.toolbar = Toolbar(self, toolbar_cb)
        self.piano_roll_frame = PianoRollFrame(
            self, lambda *args, **kwargs: self.set_dirty(True))
        self.bottombar = BottomBar(self, bottombar_cb)

        self.toolbar.pack(side=TOP, fill=X)
        self.bottombar.pack(side=BOTTOM, fill=X)
        self.piano_roll_frame.pack(fill=BOTH, expand=True)
        self.pack(fill=BOTH, expand=True)

    def _new_cmd(self):
        clear_notes = True

        if self._dirty:
            title = "New Score"
            msg = "Save changes before starting a new score?"
            answer = askyesnocancel(title, msg)

            if answer == None:
                return
            elif answer:
                if self._filepath:
                    self._save_cmd()
                else:
                    clear_notes = self._save_as_cmd()

        self.set_bottombar_length((2, 1, 0))
        self.set_bottombar_timesig((4, 4))
        if clear_notes:
            self.piano_roll_frame.grid_canvas.remove_notes('all')

        self._filepath = None
        self.set_dirty(False)

    def _open_cmd(self):
        if self._dirty:
            title = "New Score"
            msg = "Save changes before opening a new score?"
            answer = askyesnocancel(title, msg)

            if answer == None:
                return
            elif answer:
                if self._filepath:
                    self._save_cmd()
                elif not self._save_as_cmd():
                    return False

        filename = askopenfilename(
            parent=self, initialdir=self._initial_dir)
        if not filename: return False

        self._initial_dir = os.path.dirname(filename)
        self._filepath = filename

        song_data = load_song(filename)
        self.set_bottombar_length(song_data['length'])
        self.set_bottombar_timesig(song_data['timesig'])
        self.piano_roll_frame.setup(song_data['notes'])

        self.set_dirty(False)

    def _save_cmd(self):
        if not self._filepath:
            self._save_as_cmd()
        else:
            data = self.piano_roll_frame.get_song_state()
            save_song(self._filepath, data)

            self.set_dirty(False)

    def _save_as_cmd(self):
        from tkFileDialog import asksaveasfilename

        initial_file = os.path.basename(
            self._filepath or "Untitled")
        filename = asksaveasfilename(
            parent=self, initialdir=self._initial_dir,
            initialfile=initial_file)
        if not filename: return False

        self._filepath = filename
        self._initial_dir = os.path.dirname(filename)

        data = self.piano_roll_frame.get_song_state()
        save_song(filename, data)

        self.set_dirty(False)

        return True

    def _exit_cmd(self):
        if self._dirty:
            title = "New Score"
            msg = "Save changes before exiting?"
            answer = askyesnocancel(title, msg)

            if answer == None:
                return
            elif answer:
                if self._filepath:
                    self._save_cmd()
                elif not self._save_as_cmd():
                    return False

        self.quit()

    def set_snap(self, snap_value):
        self.piano_roll_frame.set_subdiv(snap_value)

    def set_zoomx(self, zoomx):
        self.piano_roll_frame.set_zoomx(zoomx)

    def set_zoomy(self, zoomy):
        self.piano_roll_frame.set_zoomy(zoomy)

    def set_canvas_length(self, length):
        self.piano_roll_frame.set_length(length)

    def set_bottombar_length(self, length):
        self.bottombar.set_length(length)

    def set_canvas_tool(self, tool):
        self.piano_roll_frame.grid_canvas.set_tool(tool)

    def set_toolbox_tool(self, value):
        self.toolbar.set_tool(value)

    def set_canvas_timesig(self, timesig):
        self.piano_roll_frame.set_timesig(timesig)
        self.bottombar.set_max_beat_count(timesig[0])

    def set_bottombar_timesig(self, timesig):
        self.bottombar.set_timesig(timesig)

    def set_dirty(self, dirty):
        self._dirty = dirty
        self._root().title(make_title(
            os.path.basename(self._filepath or "Untitled"), dirty))
