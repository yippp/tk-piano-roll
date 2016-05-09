from Tkinter import *
from ..rect import Rect
from include.custom_canvas import CustomCanvas


class CanvasKeys(CustomCanvas):

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

    LPAD = 0.35
    RPAD = 0.05

    def __init__(self, parent, state, **kwargs):
        CustomCanvas.__init__(self, parent, highlightthickness=0, **kwargs)
        self.parent = parent
        self.config(width=CanvasKeys.WIDTH)

        self._init_data(state)
        self._redraw()

    def _init_data(self, state):
        self._gstate = state
        self._update_scrollregion()

    def _redraw(self):
        cell_height = self._gstate.cell_height()
        if cell_height > 12:
            self._draw_complex_keys()
            self._draw_lines()
            self._draw_text()
        else:
            self._draw_simple_keys()
            self._draw_lines(True)
            self._draw_text(True)

    def _draw_complex_keys(self):
        canvas_width = int(self.config()['width'][4])
        lpad = round(CanvasKeys.LPAD * canvas_width)
        rpad = round(CanvasKeys.RPAD * canvas_width)
        keyboard_width = canvas_width -lpad - rpad

        pattern = "1201220"
        cell_height = self._gstate.cell_height()
        wbk_height = round(cell_height * CanvasKeys.WHITE_BIG_KEY_RATIO)
        wsk_height = round(cell_height * CanvasKeys.WHITE_SMALL_KEY_RATIO)

        height_of_octaves_in_white_keys = [5] + [7] * 10
        height_of_octaves_in_px = [4 * wsk_height + wbk_height] + [12 * cell_height] * 10

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

                self._draw_key(CanvasKeys.WHITE_KEY_LAYER, y1, y2, keyboard_width)
                if key_type in ['1', '2'] and not (nth_octave == 0 and i == 4):
                    bk_rect = Rect(centery=y1, height=cell_height)
                    self._draw_key(CanvasKeys.BLACK_KEY_LAYER,
                        bk_rect.top, bk_rect.bottom,
                        keyboard_width * CanvasKeys.BLACK_KEY_RATIO)

                sum_of_key_heights_in_px += wk_height

    def _draw_simple_keys(self):
        canvas_width = int(self.config()['width'][4])
        lpad = round(CanvasKeys.LPAD * canvas_width)
        rpad = round(CanvasKeys.RPAD * canvas_width)
        keyboard_width = canvas_width - lpad - rpad

        pattern = "101011010101"
        cell_height = self._gstate.cell_height()
        keys_in_octave = [8] + [12] * 10

        for nth_octave in range(11):
            y_offset = sum(keys_in_octave[:nth_octave + 1]) * cell_height
            for i in range(keys_in_octave[nth_octave]):
                if pattern[i] == '1':
                    layer = CanvasKeys.WHITE_KEY_LAYER
                else:
                    layer = CanvasKeys.BLACK_KEY_LAYER

                y2 = y_offset - i * cell_height
                y1 = y2 - cell_height

                self._draw_key(layer, y1, y2, keyboard_width)

    def _draw_key(self, layer, y1, y2, width):
        if layer == 1:
            color = CanvasKeys.WHITE_KEY_FILL_COLOR
        else:
            color = CanvasKeys.BLACK_KEY_FILL_COLOR

        canvas_width = int(self.config()['width'][4])
        lpad = round(CanvasKeys.LPAD * canvas_width)

        self.add_to_layer(layer, self.create_rectangle,
            (lpad, y1, lpad + width, y2),
            outline=CanvasKeys.KEY_OUTLINE_COLOR,
            fill=color, tags='rect')

    def _draw_lines(self, on_octave=False):
        canvas_width = int(self.config()['width'][4])
        lpad = round(CanvasKeys.LPAD * canvas_width)

        cell_height = self._gstate.cell_height()
        keys_in_octave = [8] + [12] * 10

        for nth_octave in range(11):
            y_offset = sum(keys_in_octave[:nth_octave + 1]) * cell_height
            for i in range(keys_in_octave[nth_octave]):
                y = y_offset - i * cell_height
                self.add_to_layer(CanvasKeys.LINE_LAYER,
                    self.create_line, (0, y, lpad, y), tags='line')

                if on_octave: break

    def _draw_text(self, on_octave=False):
        names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

        canvas_width = int(self.config()['width'][4])
        cell_height = self._gstate.cell_height()
        lpad = round(CanvasKeys.LPAD * canvas_width)

        keys_in_octaves = [8] + [12] * 10

        for nth_octave, keys_in_octave in zip(range(11), keys_in_octaves):
            y_offset = sum(keys_in_octaves[:nth_octave + 1]) * cell_height
            for i in range(keys_in_octave):
                y = y_offset - i * cell_height - max(cell_height / 2, 7)
                text = names[i] + str(8 - nth_octave)
                self.add_to_layer(CanvasKeys.TEXT_LAYER,
                    self.create_text, (lpad - 4, y),
                    text=text, anchor=E)

                if on_octave: break

    def _update_scrollregion(self):
        sr_width = int(self.config()['width'][4])
        sr_height = self._gstate.height()
        self._scrollregion = (0, 0, sr_width, sr_height)
        self.config(scrollregion=self._scrollregion)

    def _on_zoomy_change(self):
        self._update_scrollregion()
        self.delete(ALL)
        self._redraw()

    def on_update(self, new_state):
        diff = new_state.diff(self._gstate)
        self._gstate = new_state

        if 'zoomy' in diff:
            self._on_zoomy_change()