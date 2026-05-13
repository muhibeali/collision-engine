from abc import ABC, abstractmethod
from utils.vector import Vector


class BaseObject(ABC):
    def __init__(self, position: Vector, velocity: Vector, mass: float,
                 color: str = "#3498db"):
        self.position = position
        self.velocity = velocity
        self.mass = mass
        self.color = color

    @property
    @abstractmethod
    def half_extents(self) -> tuple:
        #Returns (half_width, half_height) for boundary and collision checks.
        pass

    @abstractmethod
    def update(self, dt: float):
        pass

    @abstractmethod
    def get_shape(self) -> str:
        pass
