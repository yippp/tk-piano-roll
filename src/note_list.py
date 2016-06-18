from note import Note
from helper import dummy


class NoteList(object):

    def __init__(self, notes=(), on_state_change=dummy):
        self.notes = list(notes)
        self._on_state_change = on_state_change

    def __iter__(self):
        for note in self.notes:
            yield note

    def __contains__(self, arg):
        if isinstance(arg, Note):
            return arg in self.notes
        elif isinstance(arg, (int, long)):
            return self.from_id(arg) != None

    def copy(self):
        notes = [note.copy() for note in self.notes]
        return NoteList(notes, self._on_state_change)

    def copy_selected(self):
        notes = [note.copy() for note in self.selected()]
        return NoteList(notes, self._on_state_change)

    def select(self, *ids):
        for id in ids:
            note = self.from_id(id)
            note.selected = True

    def deselect(self, *ids):
        for id in ids:
            note = self.from_id(id)
            note.selected = False

    def selected(self):
        return filter(lambda note: note.selected, self.notes)

    def ids(self):
        return [note.id for note in self.notes]

    def selected_ids(self):
        return list(set(self.ids()).intersection(
                [note.id for note in self.selected()]))

    def from_id(self, id):
        for note in self.notes:
            if note.id == id:
                return note

        return None

    def add(self, note):
        if not isinstance(note, Note):
            raise ValueError


        note.set_on_state_change_cb(
            lambda note: self._on_state_change(list(self.notes)))
        self.notes.append(note)
        self._on_state_change(list(self.notes))

    def remove(self, note):
        self.notes.remove(note)
        self._on_state_change(list(self.notes))

    def set_on_state_change_cb(self, cb):
        self._on_state_change = cb

        for note in self.notes:
            note.set_on_state_change_cb(
                lambda *args: cb(list(self.notes)))