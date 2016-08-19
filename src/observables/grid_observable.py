from src.observable import Observable, notifiable
from src.models.grid_model import GridModel

TMP_LENGTH = (2, 1, 0)


class GridObservable(Observable):

    def __init__(self, initial_state=None):
        Observable.__init__(self)

        if isinstance(initial_state, GridModel):
            self.state = initial_state
        elif initial_state is None:
            self.state = GridModel()
        else:
            raise ValueError

    @notifiable()
    def set_subdiv(self, subdiv):
        if self.state.subdiv != subdiv:
            self.state.subdiv = subdiv

    @notifiable()
    def set_zoom(self, zoom):
        if self.state.zoom != zoom:
            self.state.zoom = tuple(zoom)

    @notifiable()
    def set_timesig(self, timesig):
        if self.state.timesig != timesig:
            self.state.timesig = tuple(timesig)

    @notifiable()
    def set_end(self, end):
        if self.state.end != end:
            self.state.end = tuple(end)

    def response(self, knowledge=None):
        return [self.state.copy()], {}
