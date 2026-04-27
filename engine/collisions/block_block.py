from engine.collisions.base_collision import BaseCollision

class BlockBlockCollision(BaseCollision):

    def check(self, a, b):
        return (
            abs(a.position.x - b.position.x) < (a.width + b.width) / 2 and
            abs(a.position.y - b.position.y) < (a.height + b.height) / 2
        )

    def resolve(self, a, b):

        # -----------------------------------
        # STEP 1: Compute overlap on X and Y
        # -----------------------------------
        dx = (a.position.x - b.position.x)
        overlap_x = (a.width + b.width) / 2 - abs(dx)

        dy = (a.position.y - b.position.y)
        overlap_y = (a.height + b.height) / 2 - abs(dy)

        # -----------------------------------
        # STEP 2: Resolve smallest penetration axis
        # -----------------------------------
        if overlap_x < overlap_y:

            # Horizontal collision
            if dx > 0:
                a.position.x += overlap_x / 2
                b.position.x -= overlap_x / 2
            else:
                a.position.x -= overlap_x / 2
                b.position.x += overlap_x / 2

            # Exchange X velocities (mass-weighted)
            a.velocity.x, b.velocity.x = self._exchange(
                a.velocity.x, b.velocity.x, a.mass, b.mass
            )

        else:

            # Vertical collision
            if dy > 0:
                a.position.y += overlap_y / 2
                b.position.y -= overlap_y / 2
            else:
                a.position.y -= overlap_y / 2
                b.position.y += overlap_y / 2

            # Exchange Y velocities (mass-weighted)
            a.velocity.y, b.velocity.y = self._exchange(
                a.velocity.y, b.velocity.y, a.mass, b.mass
            )

    def _exchange(self, v1, v2, m1, m2):
        """
        1D elastic collision formula
        """
        new_v1 = (v1 * (m1 - m2) + 2 * m2 * v2) / (m1 + m2)
        new_v2 = (v2 * (m2 - m1) + 2 * m1 * v1) / (m1 + m2)
        return new_v1, new_v2