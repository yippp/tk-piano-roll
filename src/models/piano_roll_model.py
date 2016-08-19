from src.models.grid_model import GridModel
from src.models.note_list_model import NoteListModel


class PianoRollModel(object):

    def __init__(self, grid=None,
        notes=None, selection=None,
        clipboard=None, cursor=0):
        if isinstance(grid, GridModel):
            self.grid = grid
        elif grid is None:
            self.grid = GridModel()
        else:
            raise ValueError

        if isinstance(notes, NoteListModel):
            self.notes = notes
        elif notes is None:
            self.notes = NoteListModel()
        else:
            raise ValueError

        if isinstance(selection, NoteListModel):
            self.selection = selection
        elif selection is None:
            self.selection = NoteListModel()
        else:
            raise ValueError

        if isinstance(clipboard, NoteListModel):
            self.clipboard = clipboard
        elif clipboard is None:
            self.clipboard = NoteListModel()
        else:
            raise ValueError

        self.cursor = cursor

    def copy(self):
        return PianoRollModel(
            self.grid.copy(),
            self.notes.copy())
