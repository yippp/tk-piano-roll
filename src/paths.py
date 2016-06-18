import os

this_path = os.path.dirname(os.path.abspath(__file__))
format_str = "{1}{0}..{0}images{0}{2}"

ICON_IMG_PATH = format_str.format(os.sep, this_path, 'icon.gif')
TOOL_CURSOR_IMG_PATH = format_str.format(os.sep, this_path, 'cursor.gif')
TOOL_ERASER_IMG_PATH = format_str.format(os.sep, this_path, 'eraser.gif')
TOOL_PEN_IMG_PATH = format_str.format(os.sep, this_path, 'pen.gif')