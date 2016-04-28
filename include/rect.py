from vector2d import Vector2d


class Rect:

    def __init__(self, *args):
        if (len(args) == 2 and isinstance(args[0], Vector2d) and
            isinstance(args[1], Vector2d)):
                self.coords = args[0]
                self.width = args[1].x
                self.height = args[1].y
        elif (len(args) == 3 and isinstance(args[0], Vector2d) and
            all(isinstance(arg, (int, long, float)) for arg in args[1:])):
            self.coords = args[0]
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
    def coords(self):
        return self.coords

    @coords.setter
    def coords(self, *args):
        if len(args) == 1 and isinstance(args[0], Vector2d):
            self.coords = args[0]
        elif len(args) == 2 and all(isinstance(arg, (int, long)) for arg in args):
            self.coords.x = args[0]
            self.coords.y = args[1]
        else:
            raise TypeError

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

    def scale(self, factor):
        if (factor > 0):
            return Rect(self.coords * factor, self.width * factor, self.height * factor)
        else:
            raise ValueError

    def scale_ip(self, factor):
        if (factor > 0):
            self.coords *= factor
            self.width *= factor
            self.height *= factor
        else:
            raise ValueError

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