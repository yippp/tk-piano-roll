from .grid_state import GridState

TMP_LENGTH = (2, 1, 0)

class Grid(object):

    def __init__(self, beat_count=4, beat_unit=4, subdiv=0, zoomx=1,
        zoomy=1, length=TMP_LENGTH):
        self._listeners = []
        self._state = GridState(beat_count, beat_unit, subdiv,
            zoomx, zoomy, length)

    @property
    def beat_count(self):
        return self._state.beat_count

    @beat_count.setter
    def beat_count(self, value):
        self._state.beat_count = value
        self.notify()

    @property
    def beat_unit(self):
        return self._state.beat_unit

    @beat_unit.setter
    def beat_unit(self, value):
        self._state.beat_unit = value
        self.notify()

    @property
    def subdiv(self):
        return self._state.subdiv

    @subdiv.setter
    def subdiv(self, value):
        self._state.subdiv = value
        self.notify()

    @property
    def zoomx(self):
        return self._state.zoomx

    @zoomx.setter
    def zoomx(self, value):
        self._state.zoomx = value
        self.notify()

    @property
    def zoomy(self):
        return self._state.zoomy

    @zoomy.setter
    def zoomy(self, value):
        self._state.zoomy = value
        self.notify()

    @property
    def length(self):
        return self._state.length

    @length.setter
    def length(self, length):
        self._state.length = length
        self.notify()

    def get_state(self):
        return self._state.copy()

    def notify(self):
        for listener in self._listeners:
            listener(self.get_state())

    def register_listener(self, listener):
        self._listeners.append(listener)

    def unregister_listener(self, listener):
        self._listeners.remove(listener)