from rect import Rect
from helper import dummy
from const import CELL_HEIGHT_IN_PX


class Note(object):

    def __init__(self, midinumber, velocity, onset,
        duration, id=None, selected=False,
        on_state_change=dummy):
        self._id = id
        self._midinumber = midinumber
        self._velocity = velocity
        self._onset = onset
        self._duration = duration
        self._selected = selected
        self._on_state_change = on_state_change

    def __eq__(self, other):
        return self.id == other.id

    @property
    def midinumber(self):
        return self._midinumber

    @midinumber.setter
    def midinumber(self, midinumber):
        if midinumber != self._midinumber:
            self._midinumber = midinumber
            self._on_state_change(self.copy())

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, velocity):
        if velocity != self._velocity:
            self._velocity = velocity
            self._on_state_change(self.copy())

    @property
    def onset(self):
        return self._onset

    @onset.setter
    def onset(self, onset):
        if onset != self._onset:
            self._onset = onset
            self._on_state_change(self.copy())

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, duration):
        if duration != self._duration:
            self._duration = duration
            self._on_state_change(self.copy())

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, selected):
        self._selected = selected

    def set_on_state_change_cb(self, cb):
        self._on_state_change = cb

    def copy(self):
        return Note(
            self.midinumber, self.velocity,
            self.onset, self.duration,
            id=self.id, selected=self.selected,
            on_state_change=self._on_state_change)

    def rect(self):
        from helper import tick_to_px

        x = tick_to_px(self.onset)
        y = (128. - self.midinumber - 1) * CELL_HEIGHT_IN_PX
        width = tick_to_px(self.duration)
        height = CELL_HEIGHT_IN_PX

        return Rect(x, y, width, height)

