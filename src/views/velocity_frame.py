from Tkinter import *
from include.custom_spinbox import CustomSpinbox
from src.helper import dummy


class VelocityFrame(Frame):

    def __init__(self, parent, cb=dummy):
        Frame.__init__(self, parent)
        self.parent = parent
        self.cb = cb

        self._init_ui()

    def _init_ui(self):
        self.velocity_label = Label(self, text='Velocity')
        self.velocity_spinbox = CustomSpinbox(
            self, from_=0, to=127, width=4,
            callback=self._forward)
        self.velocity_spinbox.set(100)

        self.velocity_label.pack(side=LEFT)
        self.velocity_spinbox.pack(side=LEFT)

    def _forward(self):
        value = int(self.velocity_spinbox.get())
        self.cb('velocity', value)

    def set_velocity(self, value):
        self.velocity_spinbox.set(value)