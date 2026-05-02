from objects.base_object import BaseObject
from utils.vector import Vector


class Ball(BaseObject):
    def __init__(self, position: Vector, velocity: Vector, mass: float,
                 radius: float, color: str = "#3498db"):
        super().__init__(position, velocity, mass, color)
        self.radius = radius

    @property
    def half_extents(self) -> tuple:
        return (self.radius, self.radius)

    def update(self, dt: float):
        self.position = self.position + self.velocity * dt

    def get_shape(self) -> str:
        return "circle"
