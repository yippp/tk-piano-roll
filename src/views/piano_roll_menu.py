from Tkinter import *


class PianoRollMenu(Menu):

    COLOR1 = '#FCF9F1'
    COLOR2 = '#444C4E'

    def __init__(self, *args, **kwargs):
        Menu.__init__(self, *args, **kwargs)

        self._init_ui()

    def _init_ui(self):

        self._file_menu = Menu(self, tearoff=0,
            bg=PianoRollMenu.COLOR2, fg=PianoRollMenu.COLOR1,
            activebackground=PianoRollMenu.COLOR1,
            activeforeground=PianoRollMenu.COLOR2)
        self._file_menu.add_command(label='Open', command=lambda: None)
        self._file_menu.add_command(label='Save', command=lambda: None)
        self._file_menu.add_command(label='Save as...',
            command=lambda: None)
        self._file_menu.add_command(label='Exit', command=self.quit)
        self.add_cascade(label='File', menu=self._file_menu)

        self.config(relief=FLAT, bg=PianoRollMenu.COLOR2,
            fg=PianoRollMenu.COLOR1,
            activebackground=PianoRollMenu.COLOR1,
            activeforeground=PianoRollMenu.COLOR2)