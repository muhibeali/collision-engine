import math

class Vector:
    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)

    # Vector addition
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    # Vector subtraction
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    # Scalar multiplication
    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    # Magnitude
    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)

    # Normalize
    def normalize(self):
        mag = self.magnitude()
        if mag == 0:
            return Vector(0, 0)
        return Vector(self.x / mag, self.y / mag)

    # Dot product
    def dot(self, other):
        return self.x * other.x + self.y * other.y

    # Distance
    def distance_to(self, other):
        return (self - other).magnitude()

    def __repr__(self):
        return f"Vector({self.x:.2f}, {self.y:.2f})"