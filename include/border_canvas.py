from Tkinter import *

class BorderCanvas(Frame):

    def __init__(self, parent, cnvclass, *args, **kwargs):
        Frame.__init__(self, parent)
        self.parent = parent
        self._cnvclass = cnvclass
        self._args = args
        self._kwargs = kwargs

        self._init_ui()
        self._bind_event_handlers()

    def __nonzero__(self):
        return True

    def __getattr__(self, name):
        return getattr(self._canvas, name)

    def _init_ui(self):
        # dispose of canvas highlight options
        self._kwargs.pop('highlightcolor', None)
        self._kwargs.pop('highlightbackground', None)
        self._kwargs.pop('highlightthickness', None)

        borderwidth = self._kwargs.pop('borderwidth', None)
        bordercolordefault = self._kwargs.pop('bordercolordefault', None)
        bordercolorselected = self._kwargs.pop('bordercolorselected', None)
        padding = self._kwargs.pop('padding', None)

        self.config(
            highlightbackground=bordercolordefault,
            highlightcolor=bordercolorselected,
            highlightthickness=borderwidth)

        self._canvas = self._cnvclass(self, *self._args, **self._kwargs)
        self._canvas.pack(
            padx=padding, pady=padding,
            fill=BOTH, expand=True)

    def _bind_event_handlers(self):
        self.bind('<ButtonPress-1>', self._on_bttnone_press)
        self._canvas.bind(
            '<ButtonPress-1>', self._on_bttnone_press,
            add='+')

    def _on_bttnone_press(self, event):
        self._canvas.focus_set()



