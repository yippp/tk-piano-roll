from Tkinter import *
from src.helper import dummy


class AutoScrollbar(Scrollbar):
    """
    A scrollbar that hides itself if it's not needed. Only
    works if you use the grid geometry manager.
    """

    def __init__(self, parent, show_cb=dummy, unshow_cb=dummy, **kwargs):
        Scrollbar.__init__(self, parent, **kwargs)
        self.parent = parent
        self._show_cb = show_cb
        self._unshow_cb = unshow_cb

    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
            self._unshow_cb()
        else:
            self.grid()
            self._show_cb()
        Scrollbar.set(self, lo, hi)