import math

class Vector2d:

    def __init__(self, x, y):
        if (isinstance(x, (int, long, float)) and
            isinstance(y, (int, long, float))):
            self.x = x
            self.y = y
        else:
            raise TypeError

    def __eq__(self, vector):
        return self.x == vector.x and self.y == vector.y

    def __add__(self, vector):
        return Vector2d(self.x + vector.x, self.y + vector.y)

    def __mul__(self, factor):
        return Vector2d(self.x * factor, self.y * factor)

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, x):
        self.__x = x

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, y):
        self.__y = y

    def length(self):
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self):
        self.x /= self.length()
        self.y /= self.length()

