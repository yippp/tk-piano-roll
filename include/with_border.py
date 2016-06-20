from Tkinter import *

class WithBorder(Frame):

    def __init__(self, parent, widget_class, *args, **kwargs):
        Frame.__init__(self, parent)
        self.parent = parent
        self._widget_class = widget_class
        self._args = args
        self._kwargs = kwargs

        self._init_ui()
        self._bind_event_handlers()

    def __nonzero__(self):
        return True

    def __getattr__(self, name):
        return getattr(self._widget, name)

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

        self._widget = self._widget_class(self, *self._args, **self._kwargs)
        self._widget.pack(
            padx=padding, pady=padding,
            fill=BOTH, expand=True)

    def _bind_event_handlers(self):
        self.bind('<ButtonPress-1>', self._on_bttnone_press)
        self._widget.bind(
            '<ButtonPress-1>', self._on_bttnone_press,
            add='+')

    def _on_bttnone_press(self, event):
        self._widget.focus_set()



