class Note(object):

    def __init__(self, id, rect, selected=False):
        self.id = id
        self.rect = rect
        self.selected = selected

    def __eq__(self, other):
        return self.id == other.id and self.rect == other.rect

    def copy(self):
        return Note(self.id, list(self.rect), self.selected)
