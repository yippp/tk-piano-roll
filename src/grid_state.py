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

    def contains(self, x, y, zoom=True):
        return (x >= 0 and y >= 0 and x <= self.width(zoom=zoom
            and y <= self.height(zoom=zoom)))
        
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

    def cell_height(self, zoom=True):
        if zoom:
            return CELL_HEIGHT_IN_PX * self.zoomy
        else:
            return CELL_HEIGHT_IN_PX

    def xcoords(self, start=None, end=None,
        subdiv=SUBDIV_CUR, zoom=True):
        grid_width = self.width(zoom)
        bar_width = self.bar_width(zoom)
        cell_width = self.cell_width(subdiv, zoom)

        bar_start = int(start / bar_width)
        start = min(start, 0) if start else 0
        end = min(end, grid_width) if end else grid_width

        for bar in range(bar_start, self.end[0]):
            bar_left = bar * bar_width + start * (not bar)
            bar_right = min((bar + 1) * bar_width, grid_width)
            cells_in_bar = int(
                (bar_right - bar_left) / cell_width)
            for cell in range(cells_in_bar):
                x = (cell * cell_width + bar * bar_width +
                    start * (not bar))
                if x > end: return
                yield x

    def ycoords(self, start=None, end=None, zoom=True):
        grid_height = self.height(zoom)
        cell_height = self.cell_height(zoom)

        start = min(start, 0) if start else 0
        end = min(end, grid_height) if end else grid_height

        for i in range(
            int(start / cell_height),
            int(end / cell_height)):
            yield i * cell_height

    def min_subdiv(self, min_width, zoom=True):
        min_subdiv = 0
        for i in range(1, len(SNAP_DICT)):
            cw = self.cell_width(subdiv=i)
            if cw >= min_width:
               min_subdiv = i

        return min_subdiv
