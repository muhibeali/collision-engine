import math


class Vector:
    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector") -> "Vector":
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector":
        return Vector(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> "Vector":
        return Vector(self.x / scalar, self.y / scalar)

    def __neg__(self) -> "Vector":
        return Vector(-self.x, -self.y)

    def __repr__(self) -> str:
        return f"Vector({self.x:.2f}, {self.y:.2f})"

    def magnitude(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def normalize(self) -> "Vector":
        mag = self.magnitude()
        return Vector(self.x / mag, self.y / mag) if mag != 0 else Vector(0, 0)

    def dot(self, other: "Vector") -> float:
        return self.x * other.x + self.y * other.y

    def distance_to(self, other: "Vector") -> float:
        return (self - other).magnitude()
