from utils.vector import Vector
from engine.collision_engine import CollisionEngine

class PhysicsEngine:
    def __init__(self):
        self.objects = []
        self.running = False
        self.collision_engine = CollisionEngine()

    def add_object(self, obj):
        self.objects.append(obj)

    def start(self):
        self.running = True

    def pause(self):
        self.running = False

    def reset(self):
        self.objects = []

    def update(self, dt):
        if not self.running:
            return

        # Step 1: apply physics
        for obj in self.objects:
            self.apply_friction(obj, dt)
            obj.update(dt)

    # Step 2: handle collisions
        self.collision_engine.handle_collisions(self.objects)

    def apply_friction(self, obj, dt):
        # If object has no friction attribute, skip
        if not hasattr(obj, "friction"):
            return

        decay = max(0, 1 - obj.friction * dt)
        obj.velocity = obj.velocity * decay

        # Stop very small velocities (prevents infinite sliding)
        if obj.velocity.magnitude() < 0.01:
            obj.velocity = Vector(0, 0)