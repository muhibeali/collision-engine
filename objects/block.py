from objects.base_object import BaseObject
from utils.vector import Vector


class Block(BaseObject):
    def __init__(self, position: Vector, velocity: Vector, mass: float,
                 width: float, height: float, color: str = "#e74c3c"):
        super().__init__(position, velocity, mass, color)
        self.width = width
        self.height = height

    @property
    def half_extents(self) -> tuple:
        return (self.width / 2, self.height / 2)

    def update(self, dt: float):
        self.position = self.position + self.velocity * dt

    def get_shape(self) -> str:
        return "rectangle"
