from src.observable import Observable, notifiable
from src.models.note_list_model import NoteListModel
from src.models.note_model import NoteModel


class NoteListObservable(Observable):

    def __init__(self, initial_state=None):
        Observable.__init__(self)

        if isinstance(initial_state, NoteListModel):
            self.state = initial_state
        elif isinstance(initial_state, list):
            self.state = NoteListModel(initial_state)
        elif initial_state is None:
            self.state = NoteListModel()
        else:
            raise ValueError

    @notifiable()
    def add(self, *notes):
        for note in notes:
            if not isinstance(note, NoteModel):
                raise ValueError
            insert_at = len(self.state)
            for i, other in enumerate(self.state):
                if note < other:
                    break
            self.state.notes.insert(insert_at, note)

    @notifiable()
    def remove(self, *args):
        for arg in args:
            if isinstance(arg, (int, long)):
                note = self.state.get(arg)
                self.state.notes.remove(note)
            elif isinstance(arg, NoteModel):
                self.state.notes.remove(arg)
            else:
                raise ValueError

    @notifiable()
    def set(self, attr, value, *ids):
        for id in ids:
            note = self.state.get(id)
            setattr(note, attr, value)

    @notifiable()
    def change(self, d_midinumber=0, d_velocity=0,
        d_onset=0, d_duration=0, *ids):
        for note in [self.state.get(id) for id in ids]:
            note.midinumber += d_midinumber
            note.velocity += d_velocity
            note.onset += d_onset
            note.duration += d_duration

    def response(self, knowledge=None):
        return [self.state.copy()], {}
