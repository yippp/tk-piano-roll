from grid_state import GridState

TMP_LENGTH = (2, 1, 0)

class Grid(object):

    def __init__(self, subdiv=0, timesig=(4, 4), zoomx=1,
        zoomy=0.5, end=TMP_LENGTH):
        self._listeners = []
        self._state = GridState(subdiv, timesig, end,
            zoomx, zoomy)

    @property
    def timesig(self):
        return self._state.timesig

    @timesig.setter
    def timesig(self, timesig):
        if self._state.timesig != timesig:
            self._state.timesig = timesig
            self.notify()

    @property
    def subdiv(self):
        return self._state.subdiv

    @subdiv.setter
    def subdiv(self, subdiv):
        if self._state.subdiv != subdiv:
            self._state.subdiv = subdiv
            self.notify()

    @property
    def zoomx(self):
        return self._state.zoomx

    @zoomx.setter
    def zoomx(self, zoomx):
        if self._state.zoomx != zoomx:
            self._state.zoomx = zoomx
            self.notify()

    @property
    def zoomy(self):
        return self._state.zoomy

    @zoomy.setter
    def zoomy(self, zoomy):
        if self._state.zoomy != zoomy:
            self._state.zoomy = zoomy
            self.notify()

    @property
    def end(self):
        return self._state.end

    @end.setter
    def end(self, end):
        if self._state.end != end:
            self._state.end = end
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