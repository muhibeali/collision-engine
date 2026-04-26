from utils.vector import Vector
from objects.ball import Ball

class CollisionEngine:
    def __init__(self):
        pass

    def handle_collisions(self, objects):
        n = len(objects)

        for i in range(n):
            for j in range(i + 1, n):
                a = objects[i]
                b = objects[j]

                # Only handle Ball-Ball for now
                if isinstance(a, Ball) and isinstance(b, Ball):
                    if self.check_ball_collision(a, b):
                        self.resolve_ball_collision(a, b)

    def check_ball_collision(self, a, b):
        dist = a.position.distance_to(b.position)
        return dist <= (a.radius + b.radius)

    def resolve_ball_collision(self, a, b):
        # Step 1: Normal vector
        normal = (b.position - a.position).normalize()

        # Step 2: Relative velocity
        relative_velocity = a.velocity - b.velocity

        # Step 3: Velocity along normal
        vel_along_normal = relative_velocity.dot(normal)

        # If objects are moving apart, ignore
        if vel_along_normal > 0:
            return

        # Step 4: Compute impulse
        j = -(2 * vel_along_normal) / (1/a.mass + 1/b.mass)

        # Step 5: Apply impulse
        impulse = normal * j

        a.velocity = a.velocity + impulse * (1 / a.mass)
        b.velocity = b.velocity - impulse * (1 / b.mass)

        # Step 6 (IMPORTANT): Separate overlapping objects
        self.separate_objects(a, b, normal)
    
    def separate_objects(self, a, b, normal):
        overlap = (a.radius + b.radius) - a.position.distance_to(b.position)

        if overlap > 0:
            correction = normal * (overlap / 2)
            a.position = a.position - correction
            b.position = b.position + correction