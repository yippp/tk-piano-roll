import math
from helper import tick_to_px
from const import *

TMP_LENGTH = (2, 1, 0)


class GridState(object):

    NUM_OF_KEYS_IN_OCTAVE = 128

    SUBDIV_BAR = 0
    SUBDIV_CUR = -1
    SUBDIV_BU = -2
    
    def __init__(self, subdiv, beat_count, beat_unit,
        end, zoomx, zoomy):
        self.beat_count = beat_count
        self.beat_unit = beat_unit
        self.subdiv = subdiv
        self.zoomx = zoomx
        self.zoomy = zoomy
        self.end = end

    def __sub__(self, other):
        if not isinstance(other, GridState):
            raise ValueError

        def compare(attr):
            return getattr(self, attr) != getattr(other, attr)

        diff = filter(compare, vars(self).keys())

        return diff

    def copy(self):
        return GridState(self.subdiv, self.beat_count, self.beat_unit,
            self.end, self.zoomx, self.zoomy)
        
    def width(self, zoom=True):
        from helper import to_ticks

        bar, beat, tick = self.end
        zoomx = self.zoomx if zoom else 1
        return to_ticks(
            bar - 1, beat - 1, tick_to_px(tick),
            self.beat_count, self.beat_unit,
            tpq=QUARTER_NOTE_WIDTH) * zoomx

    def height(self, zoom=True):
        return GridState.NUM_OF_KEYS_IN_OCTAVE * self.cell_height(zoom=zoom)

    def bar_width(self, zoom=True):
        from helper import to_ticks
        zoomx = self.zoomx if zoom else 1

        return to_ticks(
            bpb=self.beat_count, bu=self.beat_unit,
            tpq=QUARTER_NOTE_WIDTH) * zoomx

    def cell_width(self, subdiv=SUBDIV_CUR, zoom=True):
        if subdiv in [GridState.SUBDIV_CUR, 'cur_subdiv']:
            _subdiv = self.subdiv
        elif subdiv in [GridState.SUBDIV_BU, 'bu_subdiv']:
            _subdiv = math.log(float(self.beat_unit), 2)
        else:
            _subdiv = subdiv

        bar_width = self.bar_width(zoom)

        if _subdiv in [GridState.SUBDIV_BAR, 'bar_subdiv']:
            return bar_width
        else:
            zoomx = self.zoomx if zoom else 1
            return min(
                2 ** (2 - _subdiv) * QUARTER_NOTE_WIDTH *
                zoomx, bar_width)

    def min_cell_width(self, min_width, zoom=True):
        min_cell_width = self.cell_width(0, zoom)
        for i in range(1, len(SNAP_DICT)):
            cw = self.cell_width(subdiv=i)
            if cw >= min_width:
               min_cell_width = cw

        return min_cell_width

    def cell_height(self, zoom=True):
        if zoom:
            return CELL_HEIGHT_IN_PX * self.zoomy
        else:
            return CELL_HEIGHT_IN_PX
        
    def row(self, x, zoom=True):
        return int(x / self.cell_width(zoom=zoom))

    def col(self, y, zoom=True):
        return int(y / self.cell_height(zoom=False))

    def contains(self, x, y, zoom=True):
        return (x >= 0 and y >= 0 and x <= self.width(zoom=zoom
            and y <= self.height(zoom=zoom)))