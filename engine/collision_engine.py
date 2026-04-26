from utils.vector import Vector
from objects.ball import Ball
from objects.block import Block

class CollisionEngine:
    def __init__(self):
        pass

    def handle_collisions(self, objects):
        n = len(objects)

        for i in range(n):
            for j in range(i + 1, n):
                a = objects[i]
                b = objects[j]

                # Ball-Ball
                if isinstance(a, Ball) and isinstance(b, Ball):
                    if self.check_ball_collision(a, b):
                        self.resolve_ball_collision(a, b)

                # Ball-Block
                elif isinstance(a, Ball) and isinstance(b, Block):
                    if self.check_ball_block_collision(a, b):
                        self.resolve_ball_block_collision(a, b)

                elif isinstance(a, Block) and isinstance(b, Ball):
                    if self.check_ball_block_collision(b, a):
                        self.resolve_ball_block_collision(b, a)

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
    
    def check_ball_block_collision(self, ball, block):
        # Find closest point on rectangle to circle center

        closest_x = max(block.position.x - block.width / 2,
                    min(ball.position.x, block.position.x + block.width / 2))

        closest_y = max(block.position.y - block.height / 2,
                    min(ball.position.y, block.position.y + block.height / 2))

        # Distance from circle center to closest point
        dist_x = ball.position.x - closest_x
        dist_y = ball.position.y - closest_y

        return (dist_x**2 + dist_y**2) <= (ball.radius ** 2)
    
    def resolve_ball_block_collision(self, ball, block):

        # Step 1: Find closest point on rectangle
        closest_x = max(block.position.x - block.width / 2,
                        min(ball.position.x, block.position.x + block.width / 2))

        closest_y = max(block.position.y - block.height / 2,
                        min(ball.position.y, block.position.y + block.height / 2))

        closest_point = Vector(closest_x, closest_y)

        # Step 2: Collision normal
        normal = (ball.position - closest_point)

        if normal.magnitude() == 0:
            return

        normal = normal.normalize()

        # Step 3: Reflect velocity
        v = ball.velocity
        ball.velocity = v - normal * (2 * v.dot(normal))

        # Step 4: Fix penetration (push ball out)
        overlap = ball.radius - ball.position.distance_to(closest_point)

        if overlap > 0:
            ball.position = ball.position + normal * overlap