import math
from src.helper import tick_to_px
from src.const import *


TMP_LENGTH = (2, 1, 0)


class GridModel(object):

    NUM_OF_KEYS = 128

    SUBDIV_BAR = 0
    SUBDIV_CUR = -1
    SUBDIV_BU = -2
    
    def __init__(self, subdiv=0, zoom=(1, 0.5),
        timesig=(4, 4), end=(2, 1, 0)):
        self.subdiv = subdiv
        self.zoom = tuple(zoom)
        self.timesig = tuple(timesig)
        self.end = tuple(end)

    def __repr__(self):
        return ("<GridModel (subdiv={0}, zoom={1}, "
           "timesig={2}, end={3})>".format(
            self.subdiv, self.zoom, self.timesig,
            self.end))

    def __eq__(self, other):
        if isinstance(other, GridModel):
            return (self.subdiv == other.subdiv and
                self.zoom == other.zoom and
                self.timesig == other.timesig and
                self.end == other.end)
        return NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)

    def copy(self):
        return GridModel(self.subdiv, self.zoom,
            self.timesig, self.end)

    def compare(self, other, *attr):
        for a in attr:
            if getattr(self, a) != getattr(other, a):
                return False
        return True

    def contains(self, x, y, zoomed=True):
        return (0 <= x <= self.width(zoomed) and
            0 <= y <= self.height(zoomed=zoomed))

    def width(self, zoomed=True):
        from src.helper import to_ticks

        bar, beat, tick = self.end
        beat_count, beat_unit = self.timesig
        zoomed = self.zoom[0] if zoomed else 1
        return to_ticks(
            bar - 1, beat - 1, tick_to_px(tick), beat_count,
            beat_unit, tpq=QUARTER_NOTE_WIDTH) * zoomed

    def height(self, zoomed=True):
        return (GridModel.NUM_OF_KEYS *
                self.cell_height(zoomed=zoomed))\

    def bar_width(self, zoomed=True):
        from src.helper import to_ticks

        beat_count, beat_unit = self.timesig
        zoomed = self.zoom[0] if zoomed else 1

        return to_ticks(
            bpb=beat_count, bu=beat_unit,
            tpq=QUARTER_NOTE_WIDTH) * zoomed

    def cell_width(self, subdiv=SUBDIV_CUR, zoomed=True):
        beat_unit = self.timesig[1]

        if subdiv in [GridModel.SUBDIV_CUR, 'cur_subdiv']:
            _subdiv = self.subdiv
        elif subdiv in [GridModel.SUBDIV_BU, 'bu_subdiv']:
            _subdiv = math.log(float(beat_unit), 2)
        else:
            _subdiv = subdiv

        bar_width = self.bar_width(zoomed)

        if _subdiv in [GridModel.SUBDIV_BAR, 'bar_subdiv']:
            return bar_width
        else:
            zoomed = self.zoom[0] if zoomed else 1
            return min(
                    2 ** (2 - _subdiv) * QUARTER_NOTE_WIDTH *
                    zoomed, bar_width)

    def cell_height(self, zoomed=True):
        if zoomed:
            return CELL_HEIGHT_IN_PX * self.zoom[1]
        else:
            return CELL_HEIGHT_IN_PX

    def xcoords(self, start=None, end=None,
        subdiv=SUBDIV_CUR, zoomed=True):
        grid_width = self.width(zoomed)
        bar_width = self.bar_width(zoomed)
        cell_width = self.cell_width(subdiv, zoomed)

        bar_start = int(start / bar_width)
        start = min(start, 0) if start else 0
        end = min(end, grid_width) if end else grid_width

        for bar in range(bar_start, self.end[0]):
            bar_left = bar * bar_width + start * (not bar)
            bar_right = min((bar + 1) * bar_width, grid_width)
            cells_in_bar = int(math.ceil(
                (bar_right - bar_left) / cell_width))
            for cell in range(cells_in_bar):
                x = (cell * cell_width + bar * bar_width +
                    start * (not bar))
                if x > end: return
                yield x

    def ycoords(self, start=None, end=None, zoomed=True):
        grid_height = self.height(zoomed)
        cell_height = self.cell_height(zoomed)

        start = min(start, 0) if start else 0
        end = min(end, grid_height) if end else grid_height

        for i in range(
            int(start / cell_height),
            int(end / cell_height)):
            yield i * cell_height

    def min_subdiv(self, min_width, zoomed=True):
        min_subdiv = 0
        for i in range(1, len(SNAP_DICT)):
            cw = self.cell_width(subdiv=i)
            if cw >= min_width:
               min_subdiv = i

        return min_subdiv
