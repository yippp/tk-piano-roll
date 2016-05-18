import os

this_path = os.path.dirname(os.path.abspath(__file__))
format_str = "{0}..{0}{1}{0}{2}"

IMAGES_DIRNAME = 'images'
CURSOR_TOOL_IMG_PATH = this_path + format_str.format(os.sep,
    IMAGES_DIRNAME, 'cursor.gif')
ERASER_TOOL_IMG_PATH = this_path + format_str.format(os.sep,
    IMAGES_DIRNAME, 'eraser.gif')
PEN_TOOL_IMG_PATH = this_path + format_str.format(os.sep,
    IMAGES_DIRNAME, 'pen.gif')