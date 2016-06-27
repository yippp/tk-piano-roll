import os
from Tkinter import *
from tkMessageBox import askyesnocancel
from tkFileDialog import askopenfilename
from piano_roll_menu import PianoRollMenu
from main_frame import MainFrame
from toolbar import Toolbar
from bottombar import BottomBar
from src.helper import (make_title,
    get_image_path, save_song, load_song)
from src.paths import ICON_IMG_PATH


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
        root = self._root()
        try:
            image_path = get_image_path('icon.gif')
            image = PhotoImage(file=image_path)
            root.tk.call('wm', 'iconphoto', root._w, image)
        except TclError:
            print "Couldn't load icon file"

        callbacks = self._make_callbacks()

        menu = PianoRollMenu(root, callbacks['menu'])
        root.config(menu=menu)
        root.title(make_title("Untitled", self._dirty))

        self.main_frame = MainFrame(self, callbacks['main'])
        self.toolbar = Toolbar(self, callbacks['toolbar'])
        self.bottombar = BottomBar(
            self, callbacks['bottombar'])

        self.toolbar.pack(side=TOP, fill=X)
        self.bottombar.pack(side=BOTTOM, fill=X)
        self.main_frame.pack(fill=BOTH, expand=True)
        self.pack(fill=BOTH, expand=True)

    def _cmd_save_as(self):
        from tkFileDialog import asksaveasfilename

        initial_file = os.path.basename(
            self._filepath or "Untitled")
        filename = asksaveasfilename(
            parent=self, initialdir=self._initial_dir,
            initialfile=initial_file)
        if not filename: return False

        self._filepath = filename
        self._initial_dir = os.path.dirname(filename)

        data = self.main_frame.get_song_state()
        save_song(filename, data)

        self.set_dirty(False)

        return True

    def _make_callbacks(self):
        def menu_new():
            clear_notes = True

            if self._dirty:
                title = "New Score"
                msg = ("Save changes before starting "
                    "new score?")
                answer = askyesnocancel(title, msg)

                if answer == None:
                    return
                elif answer:
                    if self._filepath:
                        menu_save()
                    else:
                        clear_notes = self._cmd_save_as()

            bottombar_set_end((2, 1, 0))
            bottombar_set_timesig((4, 4))
            if clear_notes:
                self.main_frame.grid_canvas.remove_note('all')

            self._filepath = None
            self.set_dirty(False)

        def menu_open():
            if self._dirty:
                title = "Open Score"
                msg = ("Save changes before opening a"
                    " new score?")
                answer = askyesnocancel(title, msg)

                if answer == None:
                    return
                elif answer:
                    if self._filepath:
                        menu_save()
                    elif not self._cmd_save_as():
                        return False

            filename = askopenfilename(
                parent=self, initialdir=self._initial_dir)
            if not filename: return False

            self._initial_dir = os.path.dirname(filename)
            self._filepath = filename

            song_data = load_song(filename)
            bottombar_set_end(song_data['end'])
            bottombar_set_timesig(song_data['timesig'])
            self.main_frame.setup(song_data['notes'])

            self.set_dirty(False)

        def menu_save():
            if not self._filepath:
                menu_save_as()
            else:
                data = self.main_frame.get_song_state()
                save_song(self._filepath, data)

                self.set_dirty(False)

        def menu_save_as():
            from tkFileDialog import asksaveasfilename

            initial_file = os.path.basename(
                self._filepath or "Untitled")
            filename = asksaveasfilename(
                parent=self, initialdir=self._initial_dir,
                initialfile=initial_file)
            if not filename: return False

            self._filepath = filename
            self._initial_dir = os.path.dirname(filename)

            data = self.main_frame.get_song_state()
            save_song(filename, data)

            self.set_dirty(False)

            return True

        def menu_exit():
            if self._dirty:
                title = "Exit"
                msg = "Save changes before exiting?"
                answer = askyesnocancel(title, msg)

                if answer == None:
                    return
                elif answer:
                    if self._filepath:
                        menu_save()
                    elif not self._cmd_save_as():
                        return False

            self.quit()

        def main_set_velocity(value):
            self.toolbar.velocity_frame.set_value(value)

        def main_set_zoomx(zoomx):
            self.main_frame.set_zoomx(zoomx)

        def main_set_zoomy(zoomy):
            self.main_frame.set_zoomy(zoomy)

        def toolbar_set_snap(snap):
            self.main_frame.set_subdiv(snap)

        def toolbar_set_tool(tool):
            self.main_frame.grid_canvas.set_tool(tool)

        def toolbar_set_velocity(velocity):
            self.main_frame.grid_canvas.set_velocity(
                velocity, 'sel')

        def bottombar_set_end(end):
            self.main_frame.set_end(end)

        def bottombar_set_timesig(timesig):
            self.main_frame.set_timesig(timesig)

        return {
            'menu': {
                'new': menu_new,
                'open': menu_open,
                'save': menu_save,
                'save_as': menu_save_as,
                'exit': menu_exit
            },
            'main': {
                'velocity': main_set_velocity,
                'dirty': self.set_dirty,
                'zoomx': main_set_zoomx,
                'zoomy': main_set_zoomy
            },
            'toolbar': {
                'snap': toolbar_set_snap,
                'tool': toolbar_set_tool,
                'velocity': toolbar_set_velocity
            },
            'bottombar': {
                'end': bottombar_set_end,
                'timesig': bottombar_set_timesig
            }
        }

    def set_dirty(self, dirty):
        self._dirty = dirty
        filename = self._filepath or "Untitled"
        self._root().title(
            make_title(os.path.basename(filename), dirty))