from utils.vector import Vector
from engine.collision_engine import CollisionEngine
from objects.ball import Ball
from objects.block import Block

class PhysicsEngine:
    def __init__(self):
        self.objects = []
        self.running = False
        self.collision_engine = CollisionEngine()
        self.bounds = {
        "left": -100,
        "right": 100,
        "top": 100,
        "bottom": -100
        }

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

        for obj in self.objects:
            self.apply_friction(obj, dt)
            obj.update(dt)
            self.handle_boundaries(obj)

    def apply_friction(self, obj, dt):
        # If object has no friction attribute, skip
        if not hasattr(obj, "friction"):
            return

        decay = max(0, 1 - obj.friction * dt)
        obj.velocity = obj.velocity * decay

        # Stop very small velocities (prevents infinite sliding)
        if obj.velocity.magnitude() < 0.01:
            obj.velocity = Vector(0, 0)
    
    def handle_boundaries(self, obj):

        # -----------------------
        # BALL: STOP AT EDGES
        # -----------------------
        if isinstance(obj, Ball):

            # Left wall
            if obj.position.x - obj.radius < self.bounds["left"]:
                obj.position.x = self.bounds["left"] + obj.radius
                obj.velocity.x = 0

            # Right wall
            if obj.position.x + obj.radius > self.bounds["right"]:
                obj.position.x = self.bounds["right"] - obj.radius
                obj.velocity.x = 0

            # Bottom wall
            if obj.position.y - obj.radius < self.bounds["bottom"]:
                obj.position.y = self.bounds["bottom"] + obj.radius
                obj.velocity.y = 0

            # Top wall
            if obj.position.y + obj.radius > self.bounds["top"]:
                obj.position.y = self.bounds["top"] - obj.radius
                obj.velocity.y = 0

        # -----------------------
        # BLOCK: STOP AT EDGES
        # -----------------------
        elif isinstance(obj, Block):

            half_w = obj.width / 2
            half_h = obj.height / 2

            if obj.position.x - half_w < self.bounds["left"]:
                obj.position.x = self.bounds["left"] + half_w
                obj.velocity.x = 0

            if obj.position.x + half_w > self.bounds["right"]:
                obj.position.x = self.bounds["right"] - half_w
                obj.velocity.x = 0

            if obj.position.y - half_h < self.bounds["bottom"]:
                obj.position.y = self.bounds["bottom"] + half_h
                obj.velocity.y = 0

            if obj.position.y + half_h > self.bounds["top"]:
                obj.position.y = self.bounds["top"] - half_h
                obj.velocity.y = 0