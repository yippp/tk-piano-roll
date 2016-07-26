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

        self.edit_menu = Menu(
            self, tearoff=0, bg=PianoRollMenu.COLOR2,
            fg=PianoRollMenu.COLOR1,
            activebackground=PianoRollMenu.COLOR1,
            activeforeground=PianoRollMenu.COLOR2)
        self.edit_menu.add_command(
            label='Cut', underline=0, accelerator='Ctrl+X')
        self.edit_menu.add_command(
            label='Copy', underline=0, accelerator='Ctrl+C')
        self.edit_menu.add_command(
            label='Paste', underline=0, accelerator='Ctrl+V')

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
        new_cmd = callbacks.get('new', dummy)
        open_cmd = callbacks.get('open', dummy)
        save_cmd = callbacks.get('save', dummy)
        save_as_cmd = callbacks.get('save_as', dummy)
        exit_cmd = callbacks.get('exit', dummy)
        cut_cmd = callbacks.get('cut', dummy)
        copy_cmd = callbacks.get('copy', dummy)
        paste_cmd = callbacks.get('paste', dummy)

        self.file_menu.entryconfig(0, command=new_cmd)
        self.file_menu.entryconfig(1, command=open_cmd)
        self.file_menu.entryconfig(2, command=save_cmd)
        self.file_menu.entryconfig(3, command=save_as_cmd)
        self.file_menu.entryconfig(4, command=exit_cmd)

        self.edit_menu.entryconfig(0, command=cut_cmd)
        self.edit_menu.entryconfig(1, command=copy_cmd)
        self.edit_menu.entryconfig(2, command=paste_cmd)

        self.bind_all("<Control-n>", lambda event: new_cmd())
        self.bind_all("<Control-o>", lambda event: open_cmd())
        self.bind_all("<Control-s>", lambda event: save_cmd())
        self.bind_all("<Control-w>", lambda event: exit_cmd())
        self.bind_all("<Control-x>", lambda event: cut_cmd())
        self.bind_all("<Control-c>", lambda event: copy_cmd())
        self.bind_all("<Control-v>", lambda event: paste_cmd())