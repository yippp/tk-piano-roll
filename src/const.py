from collections import OrderedDict

__snap_labels = ['Bar', '1/2', '1/4', '1/8', '1/16', '1/32', '1/64', '1/128']
__snap_values = [x for x in range(8)]

SNAP_DICT = OrderedDict([item for item in zip(__snap_labels, __snap_values)])

ZOOM_VALUES = [0.5, 0.625, 0.75, 0.875, 1, 1.25, 1.5, 1.75, 2]

DEFAULT_BAR_WIDTH_IN_PX = 512
NUM_OF_KEYS = 128