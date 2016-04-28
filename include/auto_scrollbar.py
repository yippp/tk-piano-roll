from Tkinter import *

class AutoScrollbar(Scrollbar):
    """
    A scrollbar that hides itself if it's not needed. Only
    works if you use the grid geometry manager.
    """

    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
        Scrollbar.set(self, lo, hi)