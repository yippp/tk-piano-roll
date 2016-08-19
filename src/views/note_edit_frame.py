from Tkinter import *
from pitch_frame import PitchFrame
from velocity_frame import VelocityFrame
from src.helper import dummy


class NoteEditFrame(Frame):

    def __init__(self, parent, cb=dummy):
        Frame.__init__(self, parent)
        self.parent = parent
        self._cb = cb

        self._init_ui()

    def _init_ui(self):
        self.pitch_frame = PitchFrame(self, self._cb)
        self.vel_frame = VelocityFrame(self, self._cb)

        self.pitch_frame.pack(side=LEFT)
        self.vel_frame.pack(side=LEFT, padx=4)

    def set_note(self, note):
        self.pitch_frame.set_pitch(note.midinumber)
        self.vel_frame.set_velocity(note.velocity)

    def set_state(self, state):
        self.pitch_frame.pitch_spinbox.config(state=state)
        self.vel_frame.velocity_spinbox.config(state=state)
