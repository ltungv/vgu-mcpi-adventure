import numpy as np
import math


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return Point(self.x + other.x, self.y + other.y)

    def __radd__(self, other):
        if isinstance(other, self.__class__):
            return Point(self.x + other.x, self.y + other.y)

    def __mul__(self, other):
        if isinstance(other, int):
            return Point(self.x*other, self.y*other)

    def __rmul__(self, other):
        if isinstance(other, int):
            return Point(self.x*other, self.y*other)

    def distance_to(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def get_tuple(self):
        return (self.x, self.y)


class Rectangle(object):
    def __init__(self, point1, point2):
        self.set_bounds(point1, point2)

    def __iter__(self):
        for pos_y in xrange(self.top, self.bottom):
            for pos_x in xrange(self.left, self.right):
                yield Point(pos_x, pos_y)

    def set_bounds(self, point1, point2):
        (x1, y1) = point1.get_tuple()
        (x2, y2) = point2.get_tuple()

        self.left = min(x1, x2)
        self.right = max(x1, x2)

        assert self.left < self.right, 'Incorrect coordinate'

        self.top = min(y1, y2)
        self.bottom = max(y1, y2)

        assert self.top < self.bottom, 'Incorrect coordinate'

    def overlaps(self, other):
        return (self.right >= (other.left - 1) and
                self.left <= (other.right + 1) and
                self.top <= (other.bottom + 1) and
                self.bottom >= (other.top - 1))

    def inflate(self, delta):
        return Rectangle(
                    Point(self.left - delta, self.top - delta),
                    Point(self.right + delta, self.bottom + delta)
                )

    def contains(self, point):
        if ((point.x < self.right) and
                (point.x >= self.left) and
                (point.y < self.bottom) and
                (point.y >= self.top)):
            return True
        return False


class Tiles(Rectangle):
    def __init__(self, width, height, start_x=0, start_y=0):
        super(Tiles, self).__init__(Point(start_x, start_y), Point(width, height))
        self.__tiles = np.ones((width, height), dtype=np.int16)

    def get_tile(self, pos):
        return self.__tiles[pos.x, pos.y]

    def set_tile(self, pos, tile_type=0):
        self.__tiles[pos.x][pos.y] = tile_type

    def inflate(self, delta):
        return Tiles(
                    self.right + delta, self.bottom + delta,
                    self.left - delta, self.top - delta
                )

    def odd_positions(self):
        for pos_y in xrange(1, self.bottom, 2):
            for pos_x in xrange(1, self.right, 2):
                yield Point(pos_x, pos_y)
