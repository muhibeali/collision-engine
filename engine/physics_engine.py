import copy

from utils.vector import Vector
from engine.collision_engine import CollisionEngine


class PhysicsEngine:
    # Bounds match the canvas: 700px wide, 600px tall, origin at center (350, 300)
    BOUNDS = {"left": -350, "right": 350, "bottom": -300, "top": 300}

    def __init__(self):
        self.objects = []
        self.initial_objects = []     # pristine snapshots — what gets saved / restored
        self.running = False
        self.friction = 0.02
        self.collision_engine = CollisionEngine()

    # ------------------------------------------------------------------ #
    #  Object management
    # ------------------------------------------------------------------ #
    def add_object(self, obj):
        """Append an object and record its initial state."""
        self.objects.append(obj)
        self.initial_objects.append(copy.deepcopy(obj))

    def update_object(self, index: int, obj):
        """Replace the object at index in both the live and initial lists."""
        self.objects[index] = obj
        self.initial_objects[index] = copy.deepcopy(obj)

    def remove_object(self, index: int):
        """Remove the object at index from both lists."""
        del self.objects[index]
        del self.initial_objects[index]

    # ------------------------------------------------------------------ #
    #  Simulation lifecycle
    # ------------------------------------------------------------------ #
    def start(self):
        self.running = True

    def pause(self):
        self.running = False

    def reset(self):
        """Restore every object to its initial position/velocity."""
        self.objects = [copy.deepcopy(obj) for obj in self.initial_objects]
        self.running = False

    def clear(self):
        """Remove all objects and their initial states (used before loading)."""
        self.objects.clear()
        self.initial_objects.clear()
        self.running = False

    # ------------------------------------------------------------------ #
    #  Per-frame update
    # ------------------------------------------------------------------ #
    def update(self, dt: float):
        if not self.running:
            return

        for obj in self.objects:
            self._apply_friction(obj, dt)
            obj.update(dt)

        self.collision_engine.handle_collisions(self.objects)

        for obj in self.objects:
            self._handle_boundaries(obj)

    def _apply_friction(self, obj, dt: float):
        decay = max(0.0, 1.0 - self.friction * dt)
        obj.velocity = obj.velocity * decay
        if obj.velocity.magnitude() < 0.01:
            obj.velocity = Vector(0, 0)

    def _handle_boundaries(self, obj):
        hw, hh = obj.half_extents
        b = self.BOUNDS
        hit_wall = False

        if obj.position.x - hw < b["left"]:
            obj.position.x = b["left"] + hw
            hit_wall = True

        if obj.position.x + hw > b["right"]:
            obj.position.x = b["right"] - hw
            hit_wall = True

        if obj.position.y - hh < b["bottom"]:
            obj.position.y = b["bottom"] + hh
            hit_wall = True

        if obj.position.y + hh > b["top"]:
            obj.position.y = b["top"] - hh
            hit_wall = True

        if hit_wall:
            obj.velocity = Vector(0, 0)   # full stop — no wall sliding
