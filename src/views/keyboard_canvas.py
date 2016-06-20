from Tkinter import *
from tkFont import Font
from ..rect import Rect
from include.custom_canvas import CustomCanvas
from ..const import (KEYS_IN_OCTAVE,
    KEYS_IN_LAST_OCTAVE, KEY_PATTERN)


class KeyboardCanvas(CustomCanvas):

    CANVAS_WIDTH = 128

    LAYER_KEY_BLACK = 0
    LAYER_KEY_WHITE = 1
    LAYER_TEXT = 1
    LAYER_LINE = 1

    COLOR_CANVAS_OUTLINE_NORMAL = "#000000"
    COLOR_CANVAS_OUTLINE_HIGHLIGHT = "#3399FF"
    COLOR_OUTLINE_KEY = "#000000"
    COLOR_FILL_KEY_BLACK = "#444C4E"
    COLOR_FILL_KEY_WHITE = "#FCF9F1"

    RATIO_WIDE_KEY_WHITE = 2
    RATIO_NARROW_KEY_WHITE = 1.5
    RATIO_KEY_BLACK = 0.75

    RATIO_LPAD = 0.35

    WHITE_KEYS_IN_OCTAVE = 7

    def __init__(self, parent, gstate, **kwargs):
        CustomCanvas.__init__(self, parent, **kwargs)
        self.parent = parent

        self.config(width=KeyboardCanvas.CANVAS_WIDTH)
        self._init_data(gstate)
        self._update_scrollregion()
        self._draw()
        self.yview_moveto(0)

    def _init_data(self, state):
        self._gstate = state
        self._font = Font(family='sans-serif', size=9)

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
        canvas_width = self.winfo_reqwidth()
        lpad = round(KeyboardCanvas.RATIO_LPAD * canvas_width)
        keyboard_width = canvas_width - lpad

        pattern = "1201220"
        cell_height = self._gstate.cell_height()
        wbk_height = round(cell_height * KeyboardCanvas.RATIO_WIDE_KEY_WHITE)
        wsk_height = round(cell_height * KeyboardCanvas.RATIO_NARROW_KEY_WHITE)

        height_of_octaves_in_white_keys = [5] + [KeyboardCanvas.WHITE_KEYS_IN_OCTAVE] * 10
        height_of_octaves_in_px = [4 * wsk_height + wbk_height]
        height_of_octaves_in_px += [KEYS_IN_OCTAVE * cell_height] * 10

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

                self._draw_key(KeyboardCanvas.LAYER_KEY_WHITE, y1, y2, keyboard_width)
                if key_type in ['1', '2'] and not (nth_octave == 0 and i == 4):
                    bk_rect = Rect(centery=y1, height=cell_height)
                    self._draw_key(KeyboardCanvas.LAYER_KEY_BLACK,
                        bk_rect.top, bk_rect.bottom,
                            keyboard_width * KeyboardCanvas.RATIO_KEY_BLACK)

                sum_of_key_heights_in_px += wk_height

    def _draw_simple_keys(self):
        canvas_width = self.winfo_reqwidth()
        lpad = round(KeyboardCanvas.RATIO_LPAD * canvas_width)
        keyboard_width = canvas_width - lpad

        cell_height = self._gstate.cell_height()
        keys_in_octave = [KEYS_IN_LAST_OCTAVE] + [KEYS_IN_OCTAVE] * 10

        for nth_octave in range(11):
            y_offset = sum(keys_in_octave[:nth_octave + 1]) * cell_height
            for i in range(keys_in_octave[nth_octave]):
                layer = int(KEY_PATTERN[i])
                y2 = y_offset - i * cell_height
                y1 = y2 - cell_height

                self._draw_key(layer, y1, y2, keyboard_width)

    def _draw_key(self, layer, y1, y2, width):
        if layer == 1:
            color = KeyboardCanvas.COLOR_FILL_KEY_WHITE
        else:
            color = KeyboardCanvas.COLOR_FILL_KEY_BLACK

        canvas_width = self.winfo_reqwidth()
        lpad = round(KeyboardCanvas.RATIO_LPAD * canvas_width)

        self.add_to_layer(layer, self.create_rectangle,
            (lpad, y1, lpad + width - 1, y2),
            outline=KeyboardCanvas.COLOR_OUTLINE_KEY,
            fill=color, tags='rect')

    def _draw_lines(self, on_octave=False):
        canvas_width = self.winfo_reqwidth()
        lpad = round(KeyboardCanvas.RATIO_LPAD * canvas_width)

        cell_height = self._gstate.cell_height()
        keys_in_octave = [KEYS_IN_LAST_OCTAVE] + [KEYS_IN_OCTAVE] * 10

        for nth_octave in range(11):
            y_offset = sum(keys_in_octave[:nth_octave + 1]) * cell_height
            for i in range(keys_in_octave[nth_octave]):
                y = y_offset - i * cell_height
                self.add_to_layer(KeyboardCanvas.LAYER_LINE,
                    self.create_line, (0, y, lpad, y), tags='line')

                if on_octave: break

    def _draw_text(self, on_octave=False):
        names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

        canvas_width = self.winfo_reqwidth()
        cell_height = self._gstate.cell_height()
        lpad = round(KeyboardCanvas.RATIO_LPAD * canvas_width)

        keys_in_octaves = [KEYS_IN_LAST_OCTAVE] +[KEYS_IN_OCTAVE] * 10

        for nth_octave, keys_in_octave in zip(range(11), keys_in_octaves):
            y_offset = sum(keys_in_octaves[:nth_octave + 1]) * cell_height
            y_offset -= 7 if on_octave else cell_height / 2
            for i in range(keys_in_octave):
                y = y_offset - i * cell_height
                text = names[i] + str(KEYS_IN_LAST_OCTAVE - nth_octave)
                self.add_to_layer(KeyboardCanvas.LAYER_TEXT,
                    self.create_text, (lpad - 4, y),
                    text=text, anchor=E, font=self._font)

                if on_octave: break

    def _update_scrollregion(self):
        sr_width = self.winfo_reqwidth()
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