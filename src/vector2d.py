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

    def copy(self):
        return Vector2d(self.x, self.y)

    def length(self):
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self):
        self.x /= self.length()
        self.y /= self.length()

