from engine.collisions.base_collision import BaseCollision

class BallBallCollision(BaseCollision):

    def check(self, a, b):
        dist = a.position.distance_to(b.position)
        return dist <= (a.radius + b.radius)

    def resolve(self, a, b):

        normal = (b.position - a.position).normalize()
        rel_vel = a.velocity - b.velocity
        vel_along = rel_vel.dot(normal)

        if vel_along > 0:
            return

        impulse = -(2 * vel_along) / (1/a.mass + 1/b.mass)
        impulse_vec = normal * impulse

        a.velocity = a.velocity + impulse_vec * (1 / a.mass)
        b.velocity = b.velocity - impulse_vec * (1 / b.mass)

        # separation
        overlap = (a.radius + b.radius) - a.position.distance_to(b.position)
        if overlap > 0:
            correction = normal * (overlap / 2)
            a.position = a.position - correction
            b.position = b.position + correction