from vector2d import Vector2d


class Rect(object):

    def __init__(self, *args):
        if (len(args) == 2 and isinstance(args[0], Vector2d) and
            isinstance(args[1], Vector2d)):
                self.coords = args[0].copy()
                self.width = args[1].x
                self.height = args[1].y
        elif (len(args) == 3 and isinstance(args[0], Vector2d) and
            all(isinstance(arg, (int, long, float)) for arg in args[1:])):
            self.coords = args[0].copy()
            self.width = args[1]
            self.height = args[2]
        elif (len(args) == 4 and
            all(isinstance(arg, (int, long, float)) for arg in args[1:])):
            self.coords = Vector2d(args[0], args[1])
            self.width = args[2]
            self.height = args[3]
        else:
            raise TypeError

    def __eq__(self, rect):
        return (rect.coords == self.coords and
                rect.width == self.width and
                rect.height == self.height)

    @staticmethod
    def at_origin(*args):
        return Rect(0, 0, *args)

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
        if height > 1:
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
        elif len(args) == 2 and isinstance(args[0], (int, long, float) and
            isinstance(args[1], (int, long, float))):
            x = self.coords.x + args[0]
            y = self.coords.y + args[1]
            coords = Vector2d(x, y)
        else:
            raise ValueError

        return Rect(coords, self.width, self.height)

    def move_ip(self, *args):
        if len(args) == 1 and isinstance(args[0], Vector2d):
            self.coords += args[0]
        elif len(args) == 2 and isinstance(args[0], (int, long, float) and
            isinstance(args[1], (int, long, float))):
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
        if (len(args) == 1 and isinstance(args[0], Vector2d)):
            p1 = args[0]
        elif(len(args) == 2 and isinstance(args[0], (int, long, float)) and
            isinstance(args[1], (int, long, float))):
            p1 = Vector2d(args[0], args[1])
        else:
            raise ValueError

        return (p1.x >= self.left and p1.y >= self.top and
            p1.x <= self.right and p1.y <= self.bottom)

    def collide_rect(self, rect):
        return (self.right >= rect.left and rect.right >= self.left and
            self.bottom >= rect.top and rect.bottom >= self.top)