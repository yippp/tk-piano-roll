import math
from const import SNAP_DICT

TMP_LENGTH = (2, 1, 0)

class Grid(object):

    DEFAULT_CELL_HEIGHT_IN_PX = 8
    MIN_CELL_WIDTH_IN_PX = 16
    GRID_HEIGHT_IN_CELLS = 128
    SIXTEENTH_UNIT_WIDTH = 32

    def __init__(self, beat_count=4, beat_unit=4, subdiv=0, zoomx=1, zoomy=1, length=TMP_LENGTH):
        self.beat_count = beat_count
        self.beat_unit = beat_unit
        self.subdiv = subdiv
        self.zoomx = zoomx
        self.zoomy = zoomy
        self.length = length

    @staticmethod
    def to_ticks(bars, beats, ticks, bar_width, beat_count):
        return ((bars - 1) * bar_width +
            (beats - 1) * bar_width / beat_count +
            ticks * bar_width / 256)

    def _calc_cell_width(self, subdiv, zoom=True):
        if zoom:
            return 2 ** (4 - subdiv) * Grid.SIXTEENTH_UNIT_WIDTH * self.zoomx
        else:
            return 2 ** (4 - subdiv) * Grid.SIXTEENTH_UNIT_WIDTH

    def _calc_cell_height(self, zoom=True):
        if zoom:
            return Grid.DEFAULT_CELL_HEIGHT_IN_PX * self.zoomy
        else:
            return Grid.DEFAULT_CELL_HEIGHT_IN_PX

    def _calc_max_subdiv(self, zoom=True):
        n_snap_opts = len(SNAP_DICT)

        for i in range(n_snap_opts - 1, -1, -1):
            cell_width = self._calc_cell_width(i, zoom)
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
    def beat_count(self):
        return self._beat_count

    @beat_count.setter
    def beat_count(self, value):
        self._beat_count = value

    @property
    def beat_unit(self):
        return self._beat_unit

    @beat_unit.setter
    def beat_unit(self, value):
        self._beat_unit = value

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, length):
        self._length = length

    def width(self, zoom=True):
        return Grid.to_ticks(*self.length, beat_count=self.beat_count,
            bar_width=self.bar_width(zoom))

    def height(self, zoom=True):
        return Grid.GRID_HEIGHT_IN_CELLS * self.cell_height(zoom)

    def bar_width(self, zoom=True):
        sixteenth_units_per_beat = 2 ** (4 - math.log(float(self.beat_unit), 2))
        sixteenth_units_per_bar = self.beat_count * sixteenth_units_per_beat
        if zoom:
            return Grid.SIXTEENTH_UNIT_WIDTH * sixteenth_units_per_bar * self.zoomx
        else:
            return Grid.SIXTEENTH_UNIT_WIDTH * sixteenth_units_per_bar

    def cell_width(self, zoom=True):
        return self._calc_cell_width(self.subdiv, zoom)

    def cell_height(self, zoom=True):
        return self._calc_cell_height(zoom)

    def max_cell_width(self, zoom=True):
        max_subdiv = self._calc_max_subdiv(zoom)
        return self._calc_cell_width(min(self.subdiv, max_subdiv), zoom)

    def row(self, x, zoom=True):
        return int(x / self.cell_width(zoom))

    def col(self, y, zoom=True):
        return int(y / self.cell_height(False))

    def contains(self, x, y, zoom=True):
        return (x >= 0 and y >= 0 and x <= self.width(zoom) and y <= self.height(zoom))
