from rect import Rect
from const import CELL_HEIGHT_IN_PX


class Note(object):

    def __init__(self, midinumber, velocity, onset, duration, id=None, selected=False):
        self.id = id
        self.midinumber = midinumber
        self.velocity = velocity
        self.onset = onset
        self.duration = duration
        self.selected = selected

    def __eq__(self, other):
        return self.id == other.id

    def copy(self):
        return Note(
                self.midinumber, self.velocity,
                self.onset, self.duration,
                id=self.id, selected=self.selected)

    def rect(self):
        from helper import tick_to_px

        x = tick_to_px(self.onset)
        y = (128. - self.midinumber) * CELL_HEIGHT_IN_PX
        width = tick_to_px(self.duration)
        height = CELL_HEIGHT_IN_PX

        return Rect(x, y, width, height)