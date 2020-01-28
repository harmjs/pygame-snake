import math


class Vect2d: 
    _SPLIT_CHAR = "_"

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, vect2d):
        return Vect2d(self.x + vect2d.x, self.y + vect2d.y)
    
    def __sub__(self, vect2d):
        return Vect2d(self.x - vect2d.x, self.y - vect2d.y)

    def __mul__(self, vect2d): 
        return Vect2d(self.x * vect2d.x, self.y * vect2d.y)

    def __truediv__(self, vect2d): 
        return Vect2d(self.x  / vect2d.x, self.y / vect2d.y)
    
    def __eq__(self, vect2d):
        return self.x == vect2d.x and self.y == vect2d.y

    def interate(self, callback = lambda vect2d,: vect2d):
        collection = []
        for x in range(0, int(self.x)):
            for y in range(0, int(self.y)):
                collection.append(callback(Vect2d(x, y)))
        return collection

    def to_tuple(self): 
        return (self.x, self.y)

    def serialize(self): 
        return str(self.x) + Vect2d._SPLIT_CHAR + str(self.y)

    def __str__(self):
        return "[" + str(self.x) + ", " + str(self.y) + "]"

    @classmethod
    def deserialize(cls, string):
        return cls.from_tuple([
            int(value) for value in string.split(cls._SPLIT_CHAR)
        ])

    @classmethod
    def from_tuple(cls, tuple):
        return cls(tuple[0], tuple[1])