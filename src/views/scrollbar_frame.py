from Tkinter import *
from src.helper import dummy, get_image_path


class ScrollbarFrame(Frame):

    def __init__(self, parent, orient, zoom_cb=dummy, **kwargs):
        Frame.__init__(self, parent)
        self.parent = parent

        self._init_data(orient, zoom_cb)
        self._init_ui()

    def _init_data(self, orient, zoom_cb):
        self._orient = orient
        self._zoom_cb = zoom_cb
        self._on_bttn_pressed = dummy

    def _init_ui(self):
        self.scrollbar = Scrollbar(
            self, orient=self._orient, width=14)
        self._zoom_in_img = PhotoImage(
            file=get_image_path('zoom_in.gif'))
        self.zoom_in_button = Button(
            self, image=self._zoom_in_img,
            command=lambda: self._on_bttn_pressed(True))
        self._zoom_out_img = PhotoImage(
            file=get_image_path('zoom_out.gif'))
        self.zoom_out_button = Button(
            self, image=self._zoom_out_img,
            command=lambda: self._on_bttn_pressed(False))

        if self._orient == HORIZONTAL:
            self.scrollbar.grid(row=0, column=0, sticky=W+E)
            self.zoom_in_button.grid(row=0, column=1)
            self.zoom_out_button.grid(row=0, column=2)
            self.columnconfigure(0, weight=1)
        else:
            self.scrollbar.grid(row=0, column=0, sticky=N+S)
            self.zoom_in_button.grid(row=1, column=0)
            self.zoom_out_button.grid(row=2, column=0)
            self.rowconfigure(0, weight=1)

    def on_bttn_pressed(self, listener):
        self._on_bttn_pressed = listener