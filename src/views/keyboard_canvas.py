from Tkinter import *
from tkFont import Font
from src.models.grid_model import GridModel
from src.rect import Rect
from include.custom_canvas import CustomCanvas
from src.helper import to_pitchname
from src.const import KEYS_IN_OCTAVE


class KeyboardCanvas(CustomCanvas):

    CANVAS_WIDTH = 100

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

    def __init__(self, parent, **kwargs):
        CustomCanvas.__init__(self, parent, **kwargs)
        self.parent = parent

        self._init_data()
        self._init_ui()
        self._update_scrollregion()
        self.yview_moveto(0)
        self._draw()

    def _init_data(self):
        self._grid_state = GridModel()
        self._font = Font(family='sans-serif', size=9)

    def _init_ui(self):
        self.config(
            width=KeyboardCanvas.CANVAS_WIDTH, bg='white')

    def _draw(self):
        cell_height = self._grid_state.cell_height()
        on_octave = cell_height < 14

        self._draw_keys()
        self._draw_lines(on_octave)
        self._draw_text(on_octave)

    def _draw_keys(self):
        canvas_width = self.winfo_reqwidth()
        lpad = round(KeyboardCanvas.RATIO_LPAD * canvas_width)
        keyboard_width = canvas_width - lpad

        cell_height = self._grid_state.cell_height()
        wbk_height = round(cell_height * KeyboardCanvas.RATIO_WIDE_KEY_WHITE)
        wsk_height = round(cell_height * KeyboardCanvas.RATIO_NARROW_KEY_WHITE)

        height_of_octaves_in_white_keys = [5] + [KeyboardCanvas.WHITE_KEYS_IN_OCTAVE] * 10
        height_of_octaves_in_px = [4 * wsk_height + wbk_height]
        height_of_octaves_in_px += [KEYS_IN_OCTAVE * cell_height] * 10

        pattern = "1201220"

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
        cell_height = self._grid_state.cell_height()
        lpad = round(KeyboardCanvas.RATIO_LPAD * canvas_width)

        for i, y in enumerate(self._grid_state.ycoords()):
            if on_octave and (i + 5) % 12:
                continue

            coords = (0, y + cell_height, lpad, y + cell_height)
            self.add_to_layer(KeyboardCanvas.LAYER_LINE,
                self.create_line, coords, tags='line')

    def _draw_text(self, on_octave=False):
        canvas_width = self.winfo_reqwidth()
        cell_height = self._grid_state.cell_height()
        lpad = round(KeyboardCanvas.RATIO_LPAD * canvas_width)

        for i, y in enumerate(self._grid_state.ycoords()):
            if on_octave and (i + 5) % 12:
                continue

            anchor = SE if on_octave else E
            coords = (lpad - 4, y + cell_height if on_octave else y + cell_height / 2)
            text = to_pitchname(127 - i)
            self.add_to_layer(KeyboardCanvas.LAYER_TEXT,
                self.create_text, coords, text=text,
                anchor=anchor, font=self._font)

    def _update_scrollregion(self):
        sr_width = self.winfo_reqwidth()
        sr_height = self._grid_state.height() + 1
        self._scrollregion = (0, 0, sr_width, sr_height)
        self.config(scrollregion=self._scrollregion)

    def on_state_change(self, new_grid_state):
        if self._grid_state.zoom[1] != new_grid_state.zoom[1]:
            self._grid_state = new_grid_state
            self._update_scrollregion()

            self.delete(ALL)
            self._draw()
