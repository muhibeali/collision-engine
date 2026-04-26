from objects.base_object import BaseObject

class Ball(BaseObject):
    def __init__(self, position, velocity, mass, radius):
        super().__init__(position, velocity, mass)
        self.radius = radius

    def update(self, dt):
        self.position = self.position + self.velocity * dt

    def get_shape(self):
        return "circle"