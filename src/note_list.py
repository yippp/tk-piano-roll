from note import Note


class NoteList(object):

    def __init__(self, notes=()):
        self.notes = list(notes)
        self.notes.sort(key=lambda note:
            (note.onset, -note.midinumber))

    def __nonzero__(self):
        return not not self.notes

    def __len__(self):
        return len(self.notes)

    def __contains__(self, value):
        if isinstance(value, Note):
            return value in self.notes
        elif isinstance(value, (int, long)):
            return self.from_id(value) != None

    def __getitem__(self, index):
        return self.notes[index]

    def __iter__(self):
        for note in self.notes:
            yield note

    def copy(self):
        return NoteList([note.copy() for note in self.notes])

    def selected(self):
        return NoteList(
            filter(lambda note: note.selected, self.notes))

    def select(self, *ids):
        for id in ids:
            note = self.from_id(id)
            note.selected = True

    def deselect(self, *ids):
        for id in ids:
            note = self.from_id(id)
            note.selected = False

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

        insert_at = len(self.notes)
        for i, n in enumerate(self.notes):
            if (note.midinumber > n.midinumber and
                note.onset < n.onset):
                insert_at = i
                break

        self.notes.insert(insert_at, note)

    def remove(self, note_or_id):
        if isinstance(note_or_id, Note):
            self.notes.remove(note_or_id)
        elif isinstance(note_or_id, (int, long, float)):
            note = self.from_id(note_or_id)
            self.notes.remove(note)
        else:
            raise ValueError