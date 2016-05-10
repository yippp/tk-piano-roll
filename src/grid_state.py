import math
from const import SNAP_DICT, NUM_OF_KEYS

TMP_LENGTH = (2, 1, 0)


class GridState(object):

    DEFAULT_CELL_HEIGHT_IN_PX = 12
    SIXTEENTH_UNIT_WIDTH = 32
    MIN_CELL_WIDTH_IN_PX = 16
    
    def __init__(self, beat_count=4, beat_unit=4, subdiv=0, zoomx=1,
        zoomy=1, length=TMP_LENGTH):
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
            return 2 ** (4 - subdiv) * GridState.SIXTEENTH_UNIT_WIDTH * self.zoomx
        else:
            return 2 ** (4 - subdiv) * GridState.SIXTEENTH_UNIT_WIDTH

    def _calc_cell_height(self, zoom=True):
        if zoom:
            return GridState.DEFAULT_CELL_HEIGHT_IN_PX * self.zoomy
        else:
            return GridState.DEFAULT_CELL_HEIGHT_IN_PX

    def _calc_max_subdiv(self, zoom=True):
        n_snap_opts = len(SNAP_DICT)

        for i in range(n_snap_opts - 1, -1, -1):
            cell_width = self._calc_cell_width(i, zoom)
            if cell_width >= GridState.MIN_CELL_WIDTH_IN_PX:
                return i

    def copy(self):
        return GridState(self.beat_count, self.beat_unit, self.subdiv,
            self.zoomx, self.zoomy, self.length)

    def diff(self, other):
        diff = []
        if self.beat_count != other.beat_count:
            diff.append('beat_count')
        if self.beat_unit != other.beat_unit:
            diff.append('beat unit')
        if self.subdiv != other.subdiv:
            diff.append('subdiv')
        if self.zoomx != other.zoomx:
            diff.append('zoomx')
        if self.zoomy != other.zoomy:
            diff.append('zoomy')
        if self.length != other.length:
            diff.append('length')

        return diff
        
    def width(self, zoom=True):
        return GridState.to_ticks(*self.length, beat_count=self.beat_count,
            bar_width=self.bar_width(zoom))

    def height(self, zoom=True):
        return NUM_OF_KEYS * self.cell_height(zoom)

    def bar_width(self, zoom=True):
        sixteenth_units_per_beat = 2 ** (4 - math.log(float(self.beat_unit), 2))
        sixteenth_units_per_bar = self.beat_count * sixteenth_units_per_beat
        if zoom:
            return GridState.SIXTEENTH_UNIT_WIDTH * sixteenth_units_per_bar * self.zoomx
        else:
            return GridState.SIXTEENTH_UNIT_WIDTH * sixteenth_units_per_bar

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