from vector2d import Vector2d

def _isnumber(object):
    return isinstance(object, (int, long, float))

def _is_vector2d(object):
    return isinstance(object, Vector2d)

def _is_rect(object):
    return isinstance(object, Rect)


class Rect(object):

    def __init__(self, *args, **kwargs):
        if not args:
            x = kwargs.pop('x', 0)
            y = kwargs.pop('y', 0)
            self.coords = Vector2d(x, y)
            self.width = kwargs.pop('width', 1)
            self.height = kwargs.pop('height', 1)
        elif len(args) == 2 and all(map(_is_vector2d, args)):
            self.coords = args[0].copy()
            self.width = args[1].x
            self.height = args[1].y
        elif (len(args) == 3 and _is_vector2d(args[0]) and
            all(map(_isnumber, args[1:]))):
            self.coords = args[0].copy()
            self.width = args[1]
            self.height = args[2]
        elif len(args) == 4 and all(map(_isnumber, args)):
            self.coords = Vector2d(args[0], args[1])
            self.width = args[2]
            self.height = args[3]
        else:
            raise ValueError

        for key in kwargs.keys():
            self.__setattr__(key, kwargs[key])

    def __eq__(self, rect):
        return (rect.coords == self.coords and
                rect.width == self.width and
                rect.height == self.height)

    @staticmethod
    def at_origin(width=1, height=1, **kwargs):
        remove = ['x', 'y', 'width', 'height']
        for key in remove:
            kwargs.pop(key, None)

        return Rect(0, 0, width, height, **kwargs)

    @property
    def width(self):
        return self.__width

    @width.setter
    def width(self, width):
        if width > 0:
            self.__width = width
        else:
            raise ValueError

    @property
    def height(self):
        return self.__height

    @height.setter
    def height(self, height):
        if height > 0:
            self.__height = height
        else:
            raise ValueError

    @property
    def left(self):
        return self.coords.x

    @left.setter
    def left(self, left):
        self.coords.x = left

    @property
    def top(self):
        return self.coords.y

    @top.setter
    def top(self, top):
        self.coords.y = top

    @property
    def right(self):
        return self.coords.x + self.width

    @right.setter
    def right(self, right):
        self.coords.x = right - self.width

    @property
    def bottom(self):
        return self.coords.y + self.height

    @bottom.setter
    def bottom(self, bottom):
        self.coords.y = bottom - self.height

    @property
    def centerx(self):
        return self.coords.x + int(self.width / 2)

    @centerx.setter
    def centerx(self, centerx):
        self.coords.x = centerx - int(self.width / 2)

    @property
    def centery(self):
        return self.coords.y + int(self.height / 2)

    @centery.setter
    def centery(self, centery):
        self.coords.y = centery - int(self.height / 2)

    def copy(self):
        return Rect(self.coords, self.width, self.height)

    def move(self, *args):
        if len(args) == 1 and isinstance(args[0], Vector2d):
            coords = self.coords + args[0]
        elif len(args) == 2 and all(map(_isnumber, args)):
            x = self.coords.x + args[0]
            y = self.coords.y + args[1]
            coords = Vector2d(x, y)
        else:
            raise ValueError

        return Rect(coords, self.width, self.height)

    def move_ip(self, *args):
        if len(args) == 1 and isinstance(args[0], Vector2d):
            self.coords += args[0]
        elif len(args) == 2 and all(map(_isnumber, args)):
            self.left += args[0]
            self.top += args[1]

    def scale(self, factor):
        return Rect(self.coords * factor, self.width * factor, self.height * factor)

    def scale_ip(self, factor):
        self.coords *= factor
        self.width *= factor
        self.height *= factor

    def xscale(self, xfactor):
        return Rect(self.left * xfactor, self.top, self.width * xfactor, self.height)

    def xscale_ip(self, xfactor):
        self.left *= xfactor
        self.width *= xfactor

    def yscale(self, yfactor):
        return Rect(self.left, self.top * yfactor, self.width, self.height * yfactor)

    def yscale_ip(self, yfactor):
        self.top *= yfactor
        self.height *= yfactor

    def collide_point(self, *args):
        if len(args) == 1 and _is_vector2d(args[0]):
            p1 = args[0]
        elif len(args) == 2 and all(map(_isnumber, args)):
            p1 = Vector2d(args[0], args[1])
        else:
            raise ValueError

        return (self.right > p1.x >= self.left and
            self.bottom > p1.y >= self.top)

    def collide_rect(self, *args):
        if len(args) == 1 and _is_rect(args[0]):
            rect = args[0]
        elif len(args) == 4 and all(map(_isnumber, args)):
            rect = Rect(*args)
        else:
            raise ValueError

        return not (rect.left >= self.right or
            rect.right < self.left or
            rect.top >= self.bottom or
            rect.bottom < self.top)

    def contains_rect(self, *args):
        if len(args) == 1 and _is_rect(args[0]):
            rect = args[0]
        elif len(args) == 4 and all(map(_isnumber, args)):
            rect = Rect(*args)
        else:
            raise ValueError

        return (rect.left >= self.left and
                rect.right <= self.right and
                rect.top >= self.top and
                rect.bottom <= self.bottom)