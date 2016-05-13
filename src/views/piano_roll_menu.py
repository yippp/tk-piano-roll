from Tkinter import *


class PianoRollMenu(Menu):

    COLOR1 = '#FCF9F1'
    COLOR2 = '#444C4E'

    def __init__(self, open_cmd=lambda: None, save_cmd=lambda: None,
            saveas_cmd=lambda: None, *args, **kwargs):
        Menu.__init__(self, *args, **kwargs)

        self._init_ui()
        self.file_menu.entryconfig(0, command=open_cmd)
        self.file_menu.entryconfig(1, command=save_cmd)
        self.file_menu.entryconfig(2, command=saveas_cmd)

    def _init_ui(self):
        self.file_menu = Menu(self, tearoff=0,
            bg=PianoRollMenu.COLOR2, fg=PianoRollMenu.COLOR1,
            activebackground=PianoRollMenu.COLOR1,
            activeforeground=PianoRollMenu.COLOR2)
        self.file_menu.add_command(label='Open', command=lambda: None)
        self.file_menu.add_command(label='Save', command=lambda: None)
        self.file_menu.add_command(label='Save as...',
            command=lambda: None)
        self.file_menu.add_command(label='Exit', command=self.quit)
        self.add_cascade(label='File', menu=self.file_menu)

        self.config(relief=FLAT, bg=PianoRollMenu.COLOR2,
            fg=PianoRollMenu.COLOR1,
            activebackground=PianoRollMenu.COLOR1,
            activeforeground=PianoRollMenu.COLOR2)

    def set_open_cmd(self):
        pass

    def set_openas_cmd(self):
        pass

    def set_save_cmd(self, func):
        self.file_menu.entryconfig(1, command=func)