from Tkinter import *
from include.custom_canvas import CustomCanvas
from ..helper import find_indices
from ..rect import Rect


class CanvasKeys(CustomCanvas):

    WIDTH = 100

    BLACK_KEY_LAYER = 0
    WHITE_KEY_LAYER = 1

    KEY_OUTLINE_COLOR = "#000000"
    BLACK_KEY_FILL_COLOR = "#444C4E"
    WHITE_KEY_FILL_COLOR = "#FCF9F1"

    OCT_PATTERN = '101101011010'

    def __init__(self, parent, state, **kwargs):
        CustomCanvas.__init__(self, parent, highlightthickness=0, **kwargs)
        self.parent = parent
        self.config(width=CanvasKeys.WIDTH)

        self._init_data(state)
        self._draw_pretty_keys()

    def _init_data(self, state):
        self._gstate = state
        self._update_scrollregion()

    def _draw_pretty_keys(self):
        pattern = CanvasKeys.OCT_PATTERN
        wk_indices = find_indices(pattern, '1')

        cell_height = self._gstate.cell_height()
        keyboard_width = round((int(self.config()['width'][4]) - 1) * 0.95)
        oct_height = 12 * cell_height

        x1 = self.canvasx(0)
        x2 = keyboard_width

        for nth_octave in range(11):
            y = 0
            for i in wk_indices:

                leftover = min(1, nth_octave) * cell_height / 2
                y_offset = nth_octave * oct_height - leftover
                y1 = y + y_offset

                if y1 >= self._gstate.height():
                    break

                last_key = pattern[i - 1]
                next_key = pattern[(i + 1) % len(pattern)]

                are_adjacent_keys_white = last_key == '1' or next_key == '1'
                is_first_key = nth_octave == 0 and i == 0

                if is_first_key or are_adjacent_keys_white:
                    wk_height = round(cell_height * 1.5)
                else:
                    wk_height = round(cell_height * 2)

                y2 = y1 + wk_height
                coords = (x1, y1, x2, y2)

                self.add_to_layer(CanvasKeys.WHITE_KEY_LAYER,
                    self.create_rectangle, coords,
                    outline=CanvasKeys.KEY_OUTLINE_COLOR,
                    fill=CanvasKeys.WHITE_KEY_FILL_COLOR,
                    tags='rect')

                if next_key == '0':
                    bk_width = round(keyboard_width * 0.75)
                    bk_rect = Rect(left=0, centery=y2,
                        width=bk_width, height=cell_height)
                    coords = (bk_rect.left, bk_rect.top,
                        bk_rect.right, bk_rect.bottom)

                    self.add_to_layer(CanvasKeys.BLACK_KEY_LAYER,
                        self.create_rectangle, coords,
                        outline=CanvasKeys.KEY_OUTLINE_COLOR,
                        fill=CanvasKeys.BLACK_KEY_FILL_COLOR,
                        tags='rect')

                y += wk_height

    def _draw_ugly_keys(self):
        pattern = CanvasKeys.OCT_PATTERN

        cell_height = self._gstate.cell_height()
        keyboard_width = round((int(self.config()['width'][4]) - 1) * 0.95)
        oct_height = 12 * cell_height

        x1 = self.canvasx(0)
        x2 = keyboard_width

        for nth_octave in range(11):
            y = 0
            for i in pattern:
                y_offset = nth_octave * oct_height
                y1 = y + y_offset

                if y1 >= self._gstate.height():
                    break

                if i == '0':
                    layer = CanvasKeys.BLACK_KEY_LAYER
                    fill_color = CanvasKeys.BLACK_KEY_FILL_COLOR
                else:
                    layer = CanvasKeys.WHITE_KEY_LAYER
                    fill_color = CanvasKeys.WHITE_KEY_FILL_COLOR

                y2 = y1 + cell_height
                coords = (x1, y1, x2, y2)

                self.add_to_layer(layer, self.create_rectangle,
                    coords,outline=CanvasKeys.KEY_OUTLINE_COLOR,
                    fill=fill_color, tags='rect')

                y += cell_height

    def _update_scrollregion(self):
        sr_width = int(self.config()['width'][4])
        sr_height = self._gstate.height()
        self._scrollregion = (0, 0, sr_width, sr_height)
        self.config(scrollregion=self._scrollregion)

    def _on_zoomy_change(self):
        self._update_scrollregion()
        self.delete(ALL)

        if self._gstate.cell_height() > 8:
            self._draw_pretty_keys()
        else:
            self._draw_ugly_keys()

    def on_update(self, new_state):
        diff = new_state.compare(self._gstate)
        self._gstate = new_state

        if 'zoomy' in diff:
            self._on_zoomy_change()

