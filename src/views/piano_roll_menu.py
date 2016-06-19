from Tkinter import *
from ..helper import dummy

class PianoRollMenu(Menu):

    COLOR1 = '#FCF9F1'
    COLOR2 = '#444C4E'

    def __init__(self, parent, callbacks, *args, **kwargs):
        Menu.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self._init_ui()
        self._config_commands(callbacks)

    def _init_ui(self):
        self.file_menu = Menu(
            self, tearoff=0, bg=PianoRollMenu.COLOR2,
            fg=PianoRollMenu.COLOR1,
            activebackground=PianoRollMenu.COLOR1,
            activeforeground=PianoRollMenu.COLOR2)
        self.file_menu.add_command(
            label="New", underline=0,
            accelerator="Ctrl+N")
        self.file_menu.add_command(
            label='Open', underline=0,
            accelerator="Ctrl+O")
        self.file_menu.add_command(
            label='Save', underline=0,
            accelerator="Ctrl+S")
        self.file_menu.add_command(label='Save as...')
        self.file_menu.add_command(
            label='Exit', underline=1,
            accelerator="Ctrl+W")
        self.add_cascade(
            label='File', menu=self.file_menu,
            underline=0)

        self.config(
            relief=FLAT, bg=PianoRollMenu.COLOR2,
            fg=PianoRollMenu.COLOR1,
            activebackground=PianoRollMenu.COLOR1,
            activeforeground=PianoRollMenu.COLOR2)

    def _config_commands(self, callbacks):
        new_cmd = callbacks.get('new', dummy)
        open_cmd = callbacks.get('open', dummy)
        save_cmd = callbacks.get('save', dummy)
        save_as_cmd = callbacks.get('save_as', dummy)
        exit = callbacks.get('exit', dummy)

        self.file_menu.entryconfig(
                0, command=callbacks.get('new', new_cmd))
        self.file_menu.entryconfig(
                1, command=callbacks.get('open', open_cmd))
        self.file_menu.entryconfig(
                2, command=callbacks.get('save', save_cmd))
        self.file_menu.entryconfig(
                3, command=callbacks.get('save_as', save_as_cmd))
        self.file_menu.entryconfig(
                4, command=callbacks.get('exit', exit))

        self.bind_all("<Control-n>", lambda *args, **kwargs: new_cmd())
        self.bind_all("<Control-o>", lambda *args, **kwargs: open_cmd())
        self.bind_all("<Control-s>", lambda *args, **kwargs: save_cmd())
        self.bind_all("<Control-w>", lambda *args, **kwargs: exit())