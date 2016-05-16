import math
from const import *

TMP_LENGTH = (2, 1, 0)


class GridState(object):

    MIN_CELL_WIDTH_IN_PX = 16
    NUM_OF_KEYS_IN_OCTAVE = 128

    BAR_SUBDIV = 0
    CUR_SUBDIV = -1
    BU_SUBDIV = -2
    
    def __init__(self, beat_count=4, beat_unit=4, subdiv=0, zoomx=1,
        zoomy=1, length=TMP_LENGTH):
        self.beat_count = beat_count
        self.beat_unit = beat_unit
        self.subdiv = subdiv
        self.zoomx = zoomx
        self.zoomy = zoomy
        self.length = length

    def __sub__(self, other):
        if not isinstance(other, GridState):
            raise ValueError

        def compare(attr):
            return getattr(self, attr) != getattr(other, attr)

        diff = filter(compare, vars(self).keys())

        return diff

    def _calc_max_subdiv(self, zoom=True):
        n_snap_opts = len(SNAP_DICT)

        for i in range(n_snap_opts - 1, -1, -1):
            cell_width = self.cell_width(i, zoom)
            if cell_width >= GridState.MIN_CELL_WIDTH_IN_PX:
                return i

    def copy(self):
        return GridState(self.beat_count, self.beat_unit, self.subdiv,
            self.zoomx, self.zoomy, self.length)
        
    def width(self, zoom=True):
        from helper import to_ticks

        bar_width = self.bar_width(zoom)
        bar, beat, tick = self.length

        return to_ticks(bar, beat, tick, bar_width, self.beat_count)

    def height(self, zoom=True):
        return GridState.NUM_OF_KEYS_IN_OCTAVE * self.cell_height(zoom=zoom)

    def bar_width(self, zoom=True):
        from helper import calc_ticks_per_bar
        zoomx = self.zoomx if zoom else 1

        return calc_ticks_per_bar(SIXTEENTH_UNIT_WIDTH_IN_PX,
            self.beat_count, self.beat_unit) * zoomx

    def cell_width(self, subdiv=CUR_SUBDIV, zoom=True):
        if subdiv in [GridState.CUR_SUBDIV, 'cur_subdiv']:
            _subdiv = self.subdiv
        elif subdiv in [GridState.BU_SUBDIV, 'bu_subdiv']:
            _subdiv = math.log(float(self.beat_unit), 2)
        else:
            _subdiv = subdiv

        if _subdiv in [GridState.BAR_SUBDIV, 'bar_subdiv']:
            return self.bar_width(zoom)
        else:
            zoomx = self.zoomx if zoom else 1
            return 2 ** (4 - _subdiv) * SIXTEENTH_UNIT_WIDTH_IN_PX * zoomx

    def cell_height(self, zoom=True):
        if zoom:
            return CELL_HEIGHT_IN_PX * self.zoomy
        else:
            return CELL_HEIGHT_IN_PX

    def max_cell_width(self, zoom=True):
        max_subdiv = self._calc_max_subdiv(zoom=zoom)
        return self.cell_width(min(self.subdiv, max_subdiv), zoom=zoom)
        
    def row(self, x, zoom=True):
        return int(x / self.cell_width(zoom=zoom))

    def col(self, y, zoom=True):
        return int(y / self.cell_height(zoom=False))

    def contains(self, x, y, zoom=True):
        return (x >= 0 and y >= 0 and x <= self.width(zoom=zoom
            and y <= self.height(zoom=zoom)))