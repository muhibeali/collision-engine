from engine.collisions.base_collision import BaseCollision
from utils.vector import Vector


class BallBlockCollision(BaseCollision):

    def _closest_point(self, ball, block) -> Vector:
        cx = max(block.position.x - block.width / 2,
                 min(ball.position.x, block.position.x + block.width / 2))
        cy = max(block.position.y - block.height / 2,
                 min(ball.position.y, block.position.y + block.height / 2))
        return Vector(cx, cy)

    def check(self, ball, block) -> bool:
        closest = self._closest_point(ball, block)
        return ball.position.distance_to(closest) <= ball.radius

    def resolve(self, ball, block):
        closest = self._closest_point(ball, block)
        diff = ball.position - closest
        dist = diff.magnitude()

        if dist == 0:
            # Ball center is inside the block — push out along +x as fallback
            diff = Vector(1, 0)
            dist = 1.0

        normal = diff * (1.0 / dist)  # outward from block surface toward ball

        rel_vel = ball.velocity - block.velocity
        vel_along = rel_vel.dot(normal)  # negative = ball approaching block

        if vel_along >= 0:  # already separating
            return

        j = (-2 * vel_along) / (1 / ball.mass + 1 / block.mass)
        impulse = normal * j

        ball.velocity = ball.velocity + impulse * (1 / ball.mass)
        block.velocity = block.velocity - impulse * (1 / block.mass)

        overlap = ball.radius - dist
        if overlap > 0:
            total_mass = ball.mass + block.mass
            ball.position = ball.position + normal * (overlap * block.mass / total_mass)
            block.position = block.position - normal * (overlap * ball.mass / total_mass)
