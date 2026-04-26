from objects.base_object import BaseObject

class Ball(BaseObject):
    def __init__(self, position, velocity, mass, radius, friction=0.1):
        super().__init__(position, velocity, mass)
        self.radius = radius
        self.friction = friction

    def update(self, dt):
        self.position = self.position + self.velocity * dt

    def get_shape(self):
        return "circle"