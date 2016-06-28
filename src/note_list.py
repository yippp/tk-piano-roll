from note import Note


class NoteList(object):

    def __init__(self, notes=()):
        self.notes = list(notes)

    def __nonzero__(self):
        return not not self.notes

    def __contains__(self, arg):
        if isinstance(arg, Note):
            return arg in self.notes
        elif isinstance(arg, (int, long)):
            return self.from_id(arg) != None

    def __iter__(self):
        for note in self.notes:
            yield note

    def copy(self):
        return NoteList([note.copy() for note in self.notes])

    def copy_selected(self):
        return NoteList([note.copy() for note in self.selected()])

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

        self.notes.append(note)
        self.notes.sort(key=lambda note:
            (note.onset, -note.midinumber))

    def remove(self, note):
        self.notes.remove(note)