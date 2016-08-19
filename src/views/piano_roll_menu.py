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
            label='Redo', accelerator='Ctrl+Y')
        self.edit_menu.add_separator()
        self.edit_menu.add_command(
            label='Cut', accelerator='Ctrl+X',
            state=DISABLED)
        self.edit_menu.add_command(
            label='Copy', accelerator='Ctrl+C',
            state=DISABLED)
        self.edit_menu.add_command(
            label='Paste', accelerator='Ctrl+V',
            state=DISABLED)
        self.edit_menu.add_command(label='Delete',
            state=DISABLED)
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
        def get_callback(name):
            return callbacks.get(name, dummy)

        self.file_menu.entryconfig(
            0, command=get_callback('new'))
        self.file_menu.entryconfig(
            1, command=get_callback('open'))
        self.file_menu.entryconfig(
            2, command=get_callback('save'))
        self.file_menu.entryconfig(
            3, command=get_callback('save_as'))
        self.file_menu.entryconfig(
            4, command=get_callback('exit'))

        self.edit_menu.entryconfig(
            0, command=get_callback('undo'),
            state=DISABLED)
        self.edit_menu.entryconfig(
            1, command=get_callback('redo'),
            state=DISABLED)
        self.edit_menu.entryconfig(
            3, command=get_callback('cut'))
        self.edit_menu.entryconfig(
            4, command=get_callback('copy'))
        self.edit_menu.entryconfig(
            5, command=get_callback('paste'))
        self.edit_menu.entryconfig(
            6, command=get_callback('delete'))
        self.edit_menu.entryconfig(
            7, command=get_callback('clear'))
        self.edit_menu.entryconfig(
            9, command=get_callback('select_all'))

    def set_entry_state(self, entry, state):
        self.edit_menu.entryconfig(entry, state=state)
