from collections import OrderedDict

__snap_labels = ['Bar', '1/2', '1/4', '1/8', '1/16', '1/32', '1/64', '1/128']
__snap_values = [x for x in range(8)]

SNAP_DICT = OrderedDict([item for item in zip(__snap_labels, __snap_values)])

ZOOM_X_VALUES = [0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1, 1.25, 1.5, 1.75, 2]
ZOOM_Y_VALUES = [0.5, 0.625, 0.75, 0.875, 1, 1.25, 1.5, 1.75, 2]

PITCHNAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

KEYS_IN_OCTAVE = 12
KEYS_IN_LAST_OCTAVE = 8
KEY_PATTERN = "101011010101"

CELL_HEIGHT_IN_PX = 16
TICKS_PER_QUARTER_NOTE = 480
QUARTER_NOTE_WIDTH = 120