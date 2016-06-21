class MouseState(object):

    EMPTY_AREA = 0
    UNSELECTED_NOTE = 1
    SELECTED_NOTE = 2

    def __init__(self, x=0, y=0, ctrl=False):
        self._x = x
        self._y = 0
        self._ctrl = ctrl
        self._click = MouseState.EMPTY_AREA
        self._item = 0

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        self._x = x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        self._y = y

    @property
    def ctrl(self):
        return self._ctrl

    @ctrl.setter
    def ctrl(self, ctrl):
        self._ctrl = ctrl

    @property
    def click(self):
        return self._click

    @click.setter
    def click(self, click):
        self._click = click

    @property
    def item(self):
        return self._item

    @item.setter
    def item(self, item):
        self._item = item