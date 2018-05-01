class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_tuple(self):
        return (self.x, self.y)


class Rectangle:
    def __init__(self, point1, point2):
        self.set_points(point1, point2)

    def set_points(self, point1, point2):
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
