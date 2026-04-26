from objects.base_object import BaseObject

class Block(BaseObject):
    def __init__(self, position, velocity, mass, width, height, friction=0.1):
        super().__init__(position, velocity, mass)
        self.width = width
        self.height = height
        self.friction = friction

    def update(self, dt):
        self.position = self.position + self.velocity * dt

    def get_shape(self):
        return "rectangle"