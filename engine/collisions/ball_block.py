from engine.collisions.base_collision import BaseCollision
from utils.vector import Vector

class BallBlockCollision(BaseCollision):

    def check(self, ball, block):

        closest_x = max(block.position.x - block.width / 2,
                        min(ball.position.x, block.position.x + block.width / 2))

        closest_y = max(block.position.y - block.height / 2,
                        min(ball.position.y, block.position.y + block.height / 2))

        dx = ball.position.x - closest_x
        dy = ball.position.y - closest_y

        return (dx*dx + dy*dy) <= ball.radius ** 2

    def resolve(self, ball, block):

        closest_x = max(block.position.x - block.width / 2,
                        min(ball.position.x, block.position.x + block.width / 2))

        closest_y = max(block.position.y - block.height / 2,
                        min(ball.position.y, block.position.y + block.height / 2))

        closest = Vector(closest_x, closest_y)

        normal = (ball.position - closest)

        if normal.magnitude() == 0:
            return

        normal = normal.normalize()

        ball.velocity = ball.velocity - normal * (2 * ball.velocity.dot(normal))

        overlap = ball.radius - ball.position.distance_to(closest)

        if overlap > 0:
            ball.position = ball.position + normal * overlap