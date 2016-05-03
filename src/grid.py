from const import SNAP_DICT, DEFAULT_BAR_WIDTH_IN_PX

class Grid(object):

    DEFAULT_CELL_HEIGHT_IN_PX = 8
    MIN_CELL_WIDTH_IN_PX = 20
    GRID_HEIGHT_IN_CELLS = 128

    def __init__(self, subdiv=0, zoomx=1, zoomy=1,
        length=DEFAULT_BAR_WIDTH_IN_PX):
        self._subdiv = subdiv
        self._zoomx = zoomx
        self._zoomy = zoomy
        self._length = length

    def _calc_cell_width(self, subdiv, zoomx=1):
        return DEFAULT_BAR_WIDTH_IN_PX * zoomx / 2**subdiv

    def _calc_cell_height(self, zoomy=1):
        return Grid.DEFAULT_CELL_HEIGHT_IN_PX * zoomy

    def _calc_max_subdiv(self, zoomx=1):
        n_snap_opts = len(SNAP_DICT)

        for i in range(n_snap_opts - 1, -1, -1):
            cell_width = self._calc_cell_width(i, self.zoomx)
            if cell_width >= Grid.MIN_CELL_WIDTH_IN_PX:
                return i

    @property
    def subdiv(self):
        return self._subdiv

    @subdiv.setter
    def subdiv(self, value):
        self._subdiv = value

    @property
    def zoomx(self):
        return self._zoomx

    @zoomx.setter
    def zoomx(self, value):
        self._zoomx = value

    @property
    def zoomy(self):
        return self._zoomy

    @zoomy.setter
    def zoomy(self, value):
        self._zoomy = value

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, value):
        self._length = value

    def width(self, zoom=True):
        if zoom:
            return self.length * self.zoomx
        else:
            return self.length

    def height(self, zoom=True):
        if zoom:
            return Grid.GRID_HEIGHT_IN_CELLS * self.cell_height()
        else:
            return Grid.GRID_HEIGHT_IN_CELLS * self.cell_height(False)

    def bar_width(self):
        return DEFAULT_BAR_WIDTH_IN_PX * self.zoomx

    def cell_width(self, zoom=True):
        if zoom:
            return self._calc_cell_width(self.subdiv, self.zoomx)
        else:
            return self._calc_cell_width(self.subdiv)

    def cell_height(self, zoom=True):
        if zoom:
            return self._calc_cell_height(self.zoomy)
        else:
            return self._calc_cell_height()

    def max_cell_width(self):
        max_subdiv = self._calc_max_subdiv(self.zoomx)
        return self._calc_cell_width(min(self.subdiv, max_subdiv), self.zoomx)

    def gridx(self, x):
        return x * self.zoomx

    def gridy(self, y):
        return y * self.zoomy

    def row(self, x):
        return int(x / self.cell_width())

    def col(self, y):
        return int(y / self.cell_height())

    def contains(self, x, y):
        return (x >= 0 and y >= 0 and x <= self.width() and y <= self.height())