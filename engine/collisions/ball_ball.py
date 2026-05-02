from engine.collisions.base_collision import BaseCollision


class BallBallCollision(BaseCollision):

    def check(self, a, b) -> bool:
        return a.position.distance_to(b.position) <= (a.radius + b.radius)

    def resolve(self, a, b):
        normal = (b.position - a.position).normalize()
        rel_vel = a.velocity - b.velocity
        vel_along = rel_vel.dot(normal)  # positive = a approaching b

        if vel_along <= 0:  # already separating
            return

        j = (2 * vel_along) / (1 / a.mass + 1 / b.mass)

        a.velocity = a.velocity - normal * (j / a.mass)
        b.velocity = b.velocity + normal * (j / b.mass)

        overlap = (a.radius + b.radius) - a.position.distance_to(b.position)
        if overlap > 0:
            correction = normal * (overlap / 2)
            a.position = a.position - correction
            b.position = b.position + correction
