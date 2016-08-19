class Stack(list):

    def __init__(self, iterable=(), maxsize=None):
        list.__init__(self, iterable)

        self._maxsize = maxsize
        self._pointer = 0

    @property
    def size(self):
        return len(self)

    @property
    def current(self):
        return self[-self._pointer - 1]

    @property
    def top(self):
        return self[-1]

    @property
    def bottom(self):
        return self[0]

    @property
    def pointer(self):
        return self._pointer

    @pointer.setter
    def pointer(self, pointer):
        self._pointer = pointer

    def append(self, object):
        if self._maxsize and self.size >= self._maxsize:
            del self[0]
        for i in range(self._pointer):
            del self[-1]
        self._pointer = 0

        list.append(self, object)

