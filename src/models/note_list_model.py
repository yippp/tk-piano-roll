from note_model import NoteModel


class NoteListModel(object):

    def __init__(self, notes=()):
        self.notes = list(notes)
        self.notes.sort(key=lambda note:
            (note.onset, -note.midinumber))

    def __len__(self):
        return len(self.notes)

    def __nonzero__(self):
        return not not self.notes

    def __getitem__(self, index):
        return self.notes[index]

    def __contains__(self, other):
        if isinstance(other, NoteModel):
            for note in self.notes:
                if note == other:
                    return True
            return False
        return NotImplemented

    def __iter__(self):
        for note in self.notes:
            yield note

    def __eq__(self, other):
        if isinstance(other, NoteListModel):
            return sorted(self.notes) == sorted(other.notes)
        return NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)

    def __sub__(self, other):
        if isinstance(other, NoteListModel):
            return NoteListModel(
                list(set(self.notes) - set(other.notes)))
        return NotImplemented

    def __repr__(self):
        return  "<NoteListModel ({0})>".format(', '.join(
            str(note) for note in self))

    @property
    def ids(self):
        return [note.id for note in self.notes]

    def copy(self):
        return NoteListModel(
            [note.copy() for note in self.notes])

    def get(self, id):
        from_id = None

        for note in self.notes:
            if note.id == id:
                from_id = note
                break

        return from_id
