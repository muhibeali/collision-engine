from abc import ABC, abstractmethod
from utils.vector import Vector

class BaseObject(ABC):
    def __init__(self, position, velocity, mass):
        self.position = position      # Vector
        self.velocity = velocity      # Vector
        self.mass = mass

    @abstractmethod
    def update(self, dt):
        pass

    @abstractmethod
    def get_shape(self):
        pass