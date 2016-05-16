from Tkinter import *
from tkFont import Font
from ..rect import Rect
from include.custom_canvas import CustomCanvas


class KeyboardCanvas(CustomCanvas):

    WIDTH = 128

    BLACK_KEY_LAYER = 0
    WHITE_KEY_LAYER = 1
    TEXT_LAYER = 1
    LINE_LAYER = 1

    KEY_OUTLINE_COLOR = "#000000"
    BLACK_KEY_FILL_COLOR = "#444C4E"
    WHITE_KEY_FILL_COLOR = "#FCF9F1"

    WHITE_BIG_KEY_RATIO = 2
    WHITE_SMALL_KEY_RATIO = 1.5
    BLACK_KEY_RATIO = 0.75

    LPAD_RATIO = 0.35

    KEYS_IN_OCTAVE = 12
    WHITE_KEYS_IN_OCTAVE = 7


    def __init__(self, parent, gstate, **kwargs):
        CustomCanvas.__init__(self, parent, **kwargs)
        self.parent = parent

        self._init_ui()
        self._init_data(gstate)

        self._update_scrollregion()
        self._draw()

    def _init_ui(self):
        self.config(bd=2, relief=SUNKEN)

    def _init_data(self, state):
        self._gstate = state
        self._font = Font(family='sans-serif', size=9)
        self.config(width=KeyboardCanvas.WIDTH)

    def _draw(self):
        cell_height = self._gstate.cell_height()

        if cell_height >= 14:
            self._draw_complex_keys()
            self._draw_lines()
            self._draw_text()
        else:
            self._draw_simple_keys()
            self._draw_lines(True)
            self._draw_text(True)

    def _draw_complex_keys(self):
        bd = int(self.config()['borderwidth'][4])
        canvas_width = self.winfo_reqwidth() - bd * 2
        lpad = round(KeyboardCanvas.LPAD_RATIO * canvas_width)
        keyboard_width = canvas_width - lpad

        pattern = "1201220"
        cell_height = self._gstate.cell_height()
        wbk_height = round(cell_height * KeyboardCanvas.WHITE_BIG_KEY_RATIO)
        wsk_height = round(cell_height * KeyboardCanvas.WHITE_SMALL_KEY_RATIO)

        height_of_octaves_in_white_keys = [5] + [KeyboardCanvas.WHITE_KEYS_IN_OCTAVE] * 10
        height_of_octaves_in_px = [4 * wsk_height + wbk_height]
        height_of_octaves_in_px += [KeyboardCanvas.KEYS_IN_OCTAVE * cell_height] * 10

        for nth_octave in range(11):
            y_offset = sum(height_of_octaves_in_px[:nth_octave])
            px_in_octave = height_of_octaves_in_px[nth_octave]
            white_keys_in_octave = height_of_octaves_in_white_keys[nth_octave]

            sum_of_key_heights_in_px = 0
            for i in range(white_keys_in_octave):
                key_type = pattern[i]
                wk_height = wbk_height if key_type == '2' else wsk_height

                y2 = y_offset + px_in_octave - sum_of_key_heights_in_px
                y1 = max(0, y2 - wk_height)

                self._draw_key(KeyboardCanvas.WHITE_KEY_LAYER, y1, y2, keyboard_width)
                if key_type in ['1', '2'] and not (nth_octave == 0 and i == 4):
                    bk_rect = Rect(centery=y1, height=cell_height)
                    self._draw_key(KeyboardCanvas.BLACK_KEY_LAYER,
                        bk_rect.top, bk_rect.bottom,
                        keyboard_width * KeyboardCanvas.BLACK_KEY_RATIO)

                sum_of_key_heights_in_px += wk_height

    def _draw_simple_keys(self):
        bd = int(self.config()['borderwidth'][4])
        canvas_width = self.winfo_reqwidth() - bd * 2
        lpad = round(KeyboardCanvas.LPAD_RATIO * canvas_width)
        keyboard_width = canvas_width - lpad

        pattern = "101011010101"
        cell_height = self._gstate.cell_height()
        keys_in_octave = [8] + [KeyboardCanvas.KEYS_IN_OCTAVE] * 10

        for nth_octave in range(11):
            y_offset = sum(keys_in_octave[:nth_octave + 1]) * cell_height
            for i in range(keys_in_octave[nth_octave]):
                layer = int(pattern[i])
                y2 = y_offset - i * cell_height
                y1 = y2 - cell_height

                self._draw_key(layer, y1, y2, keyboard_width)

    def _draw_key(self, layer, y1, y2, width):
        if layer == 1:
            color = KeyboardCanvas.WHITE_KEY_FILL_COLOR
        else:
            color = KeyboardCanvas.BLACK_KEY_FILL_COLOR

        bd = int(self.config()['borderwidth'][4])
        canvas_width = self.winfo_reqwidth() - bd * 2
        lpad = round(KeyboardCanvas.LPAD_RATIO * canvas_width)

        self.add_to_layer(layer, self.create_rectangle,
            (lpad, y1, lpad + width - 1, y2),
            outline=KeyboardCanvas.KEY_OUTLINE_COLOR,
            fill=color, tags='rect')

    def _draw_lines(self, on_octave=False):
        bd = int(self.config()['borderwidth'][4])
        canvas_width = self.winfo_reqwidth() - bd * 2
        lpad = round(KeyboardCanvas.LPAD_RATIO * canvas_width)

        cell_height = self._gstate.cell_height()
        keys_in_octave = [8] + [KeyboardCanvas.KEYS_IN_OCTAVE] * 10

        for nth_octave in range(11):
            y_offset = sum(keys_in_octave[:nth_octave + 1]) * cell_height
            for i in range(keys_in_octave[nth_octave]):
                y = y_offset - i * cell_height
                self.add_to_layer(KeyboardCanvas.LINE_LAYER,
                    self.create_line, (0, y, lpad, y), tags='line')

                if on_octave: break

    def _draw_text(self, on_octave=False):
        names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

        bd = int(self.config()['borderwidth'][4])
        canvas_width = self.winfo_reqwidth() - bd * 2
        cell_height = self._gstate.cell_height()
        lpad = round(KeyboardCanvas.LPAD_RATIO * canvas_width)

        keys_in_octaves = [8] + [KeyboardCanvas.KEYS_IN_OCTAVE] * 10

        for nth_octave, keys_in_octave in zip(range(11), keys_in_octaves):
            y_offset = sum(keys_in_octaves[:nth_octave + 1]) * cell_height
            y_offset -= 7 if on_octave else cell_height / 2
            for i in range(keys_in_octave):
                y = y_offset - i * cell_height
                text = names[i] + str(8 - nth_octave)
                self.add_to_layer(KeyboardCanvas.TEXT_LAYER,
                    self.create_text, (lpad - 4, y),
                    text=text, anchor=E, font=self._font)

                if on_octave: break

    def _update_scrollregion(self):
        bd = int(self.config()['borderwidth'][4])
        sr_width = self.winfo_reqwidth() - bd * 2
        sr_height = self._gstate.height() + 1
        self._scrollregion = (0, 0, sr_width, sr_height)
        self.config(scrollregion=self._scrollregion)

    def _on_zoomy_change(self):
        self.delete(ALL)
        self._update_scrollregion()
        self._draw()

    def on_update(self, new_gstate):
        diff = self._gstate - new_gstate
        self._gstate = new_gstate

        if 'zoomy' in diff:
            self._on_zoomy_change()