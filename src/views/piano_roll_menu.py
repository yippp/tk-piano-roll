from Tkinter import *
from src.helper import dummy


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
            label="New", accelerator="Ctrl+N")
        self.file_menu.add_command(
            label='Open', accelerator="Ctrl+O")
        self.file_menu.add_command(
            label='Save', accelerator="Ctrl+S")
        self.file_menu.add_command(label='Save as...')
        self.file_menu.add_command(
            label='Exit', accelerator="Ctrl+W")

        self.edit_menu = Menu(
            self, tearoff=0, bg=PianoRollMenu.COLOR2,
            fg=PianoRollMenu.COLOR1,
            activebackground=PianoRollMenu.COLOR1,
            activeforeground=PianoRollMenu.COLOR2)
        self.edit_menu.add_command(
            label='Undo', accelerator='Ctrl+Z')
        self.edit_menu.add_command(
            label='Redo', accelerator='Ctrl+Shift+Z')
        self.edit_menu.add_separator()
        self.edit_menu.add_command(
            label='Cut', accelerator='Ctrl+X')
        self.edit_menu.add_command(
            label='Copy', accelerator='Ctrl+C')
        self.edit_menu.add_command(
            label='Paste', accelerator='Ctrl+V')
        self.edit_menu.add_command(label='Delete')
        self.edit_menu.add_command(label='Clear')
        self.edit_menu.add_separator()
        self.edit_menu.add_command(
            label='Select All', accelerator='Ctrl+A')

        self.add_cascade(
            label='File', menu=self.file_menu, underline=0)
        self.add_cascade(
            label='Edit', menu=self.edit_menu, underline=0)

        self.config(
            relief=FLAT, bg=PianoRollMenu.COLOR2,
            fg=PianoRollMenu.COLOR1,
            activebackground=PianoRollMenu.COLOR1,
            activeforeground=PianoRollMenu.COLOR2)

    def _config_commands(self, callbacks):
        new = callbacks.get('new', dummy)
        open = callbacks.get('open', dummy)
        save = callbacks.get('save', dummy)
        save_as = callbacks.get('save_as', dummy)
        exit = callbacks.get('exit', dummy)
        cut = callbacks.get('cut', dummy)
        copy = callbacks.get('copy', dummy)
        paste = callbacks.get('paste', dummy)
        delete = callbacks.get('delete', dummy)
        clear = callbacks.get('clear', dummy)
        select_all = callbacks.get('select_all', dummy)

        self.file_menu.entryconfig(0, command=new)
        self.file_menu.entryconfig(1, command=open)
        self.file_menu.entryconfig(2, command=save)
        self.file_menu.entryconfig(3, command=save_as)
        self.file_menu.entryconfig(4, command=exit)

        self.edit_menu.entryconfig(3, command=cut)
        self.edit_menu.entryconfig(4, command=copy)
        self.edit_menu.entryconfig(5, command=paste)
        self.edit_menu.entryconfig(6, command=delete)
        self.edit_menu.entryconfig(7, command=clear)
        self.edit_menu.entryconfig(9, command=select_all)