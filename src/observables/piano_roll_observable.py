from src.observable import Observable, notifiable
from src.models.piano_roll_model import PianoRollModel


OBS_GRID = 0b00001
OBS_NOTE = 0b00010
OBS_SELECTION = 0b00100
OBS_CLIPBOARD = 0b01000
OBS_CURSOR = 0b10000


class PianoRollObservable(Observable):

    def __init__(self, initial_state=None):
        Observable.__init__(self)

        if isinstance(initial_state, PianoRollModel):
            self.state = initial_state
        elif initial_state is None:
            self.state = PianoRollModel()
        else:
            raise ValueError

    @notifiable(OBS_GRID)
    def set_grid(self, grid):
        self.state.grid = grid

    @notifiable(OBS_NOTE)
    def set_notes(self, notes):
        self.state.notes = notes

    @notifiable(OBS_SELECTION)
    def set_selection(self, selection):
        self.state.selection = selection

    @notifiable(OBS_CLIPBOARD)
    def set_clipboard(self, clipboard):
        self.state.clipboard = clipboard

    @notifiable(OBS_CURSOR)
    def set_cursor(self, cursor):
        self.state.cursor = cursor

    def register_observer(self, callable, mask=None):
        if not isinstance(mask, (int, long)) and 0 <= mask < 8:
            raise ValueError("tag must be either"
            " OBS_GRID, OBS_NOTE or OBS_SEL")
        Observable.register_observer(self, callable, mask)

    def response(self, knowledge=None):
        args = []
        if knowledge & OBS_GRID == OBS_GRID:
            args.append(self.state.grid.copy())
        if knowledge & OBS_NOTE == OBS_NOTE:
            args.append(self.state.notes.copy())
        if knowledge & OBS_SELECTION == OBS_SELECTION:
            args.append(self.state.selection.copy())
        if knowledge & OBS_CLIPBOARD == OBS_CLIPBOARD:
            args.append(self.state.clipboard.copy())
        if knowledge & OBS_CURSOR == OBS_CURSOR:
            args.append(self.state.cursor)

        return args, {}
