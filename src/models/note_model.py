from functools import total_ordering
from src.rect import Rect
from src.const import CELL_HEIGHT_IN_PX


@total_ordering
class NoteModel(object):

    def __init__(self, midinumber, velocity,
        onset, duration, id=None):
        self._id = id
        self._midinumber = midinumber
        self._velocity = velocity
        self._onset = onset
        self._duration = duration

    def __eq__(self, other):
        if isinstance(other, NoteModel):
            return (self.midinumber == other.midinumber and
                self.velocity == other.velocity and
                self.onset == other.onset and
                self.duration == other.duration)
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, NoteModel):
            return (self.onset < other.onset or
                (self.onset == other.onset and
                self.midinumber > other.midinumber))

    def __repr__(self):
        return ("<NoteModel (id={0}, midinumber={1}, "
            "velocity={2}, onset={3}, duration={4})>".format(
            self.id, self.midinumber, self.velocity,
            self.onset, self.duration))

    @property
    def midinumber(self):
        return self._midinumber

    @midinumber.setter
    def midinumber(self, midinumber):
        if midinumber != self._midinumber:
            self._midinumber = midinumber

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, velocity):
        if velocity != self._velocity:
            self._velocity = velocity

    @property
    def onset(self):
        return self._onset

    @onset.setter
    def onset(self, onset):
        if onset != self._onset:
            self._onset = onset

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, duration):
        if duration != self._duration:
            self._duration = duration

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def rect(self):
        from src.helper import tick_to_px

        x = tick_to_px(self.onset)
        y = (128. - self.midinumber - 1) * CELL_HEIGHT_IN_PX
        width = tick_to_px(self.duration)
        height = CELL_HEIGHT_IN_PX

        return Rect(x, y, width, height)

    def copy(self):
        return NoteModel(
            self.midinumber, self.velocity,
            self.onset, self.duration,
            self.id)

    def to_tuple(self):
        return (self.midinumber, self.velocity,
            self.onset, self.duration)

