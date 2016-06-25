import os

this_path = os.path.dirname(os.path.abspath(__file__))
format_str = "{1}{0}..{0}images{0}{2}"

ICON_IMG_PATH = format_str.format(os.sep, this_path, 'icon.gif')
SEL_IMG_PATH = format_str.format(os.sep, this_path, 'sel.gif')
PEN_IMG_PATH = format_str.format(os.sep, this_path, 'pen.gif')
ERASER_IMG_PATH = format_str.format(os.sep, this_path, 'eraser.gif')

CURSOR_SEL_IMG_PATH = format_str.format(os.sep, this_path, 'sel.xbm')
CURSOR_PEN_IMG_PATH = format_str.format(os.sep, this_path, 'pen.xbm')
CURSOR_ERASER_IMG_PATH = format_str.format(os.sep, this_path, 'eraser.xbm')