from Tkinter import *
from piano_roll_canvas import PianoRollCanvas
from include.auto_scrollbar import AutoScrollbar


class PianoRollFrame(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent

        self._init_ui()
        self._bind_event_handlers()

    def _init_ui(self):
        self._hbar = AutoScrollbar(self, orient=HORIZONTAL)
        self._vbar = AutoScrollbar(self, orient=VERTICAL)

        self._canvas = PianoRollCanvas(self, xscrollcommand=self._hbar.set,
            yscrollcommand=self._vbar.set)
        self._hbar.config(command=self._canvas.xview)
        self._vbar.config(command=self._canvas.yview)

        self._hbar.grid(row=1, column=0, sticky=E+W)
        self._vbar.grid(row=0, column=1, sticky=N+S)
        self._canvas.grid(row=0, column=0, sticky=N+S+E+W)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.focus_set()

    def _bind_event_handlers(self):
        self.bind('<Control-a>', self._on_ctrl_a)
        self.bind('<Delete>', self._on_delete)

    def _on_ctrl_a(self, event):
        self._canvas.select_rects(PianoRollCanvas.ALL)
        self.parent.set_toolbox_tool(PianoRollCanvas.SELECT_TOOL)

    def _on_delete(self, event):
        self._canvas.delete_rects(PianoRollCanvas.SELECTED)

    def set_subdiv(self, value):
        self._canvas.set_subdiv(value)

    def set_zoomx(self, value):
        self._canvas.set_zoomx(value)

    def set_zoomy(self, value):
        self._canvas.set_zoomy(value)

    def set_length(self, value):
        self._canvas.set_length(value)

    def set_tool(self, value):
        self._canvas.set_tool(value)