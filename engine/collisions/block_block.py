from engine.collisions.base_collision import BaseCollision


class BlockBlockCollision(BaseCollision):

    def check(self, a, b) -> bool:
        return (
            abs(a.position.x - b.position.x) < (a.width + b.width) / 2 and
            abs(a.position.y - b.position.y) < (a.height + b.height) / 2
        )

    def resolve(self, a, b):
        dx = a.position.x - b.position.x
        dy = a.position.y - b.position.y
        overlap_x = (a.width + b.width) / 2 - abs(dx)
        overlap_y = (a.height + b.height) / 2 - abs(dy)

        if overlap_x < overlap_y:
            sign = 1 if dx > 0 else -1
            # Skip if already separating along x
            if (a.velocity.x - b.velocity.x) * sign > 0:
                return
            a.position.x += overlap_x / 2 * sign
            b.position.x -= overlap_x / 2 * sign
            a.velocity.x, b.velocity.x = self._elastic_1d(
                a.velocity.x, b.velocity.x, a.mass, b.mass
            )
        else:
            sign = 1 if dy > 0 else -1
            # Skip if already separating along y
            if (a.velocity.y - b.velocity.y) * sign > 0:
                return
            a.position.y += overlap_y / 2 * sign
            b.position.y -= overlap_y / 2 * sign
            a.velocity.y, b.velocity.y = self._elastic_1d(
                a.velocity.y, b.velocity.y, a.mass, b.mass
            )

    @staticmethod
    def _elastic_1d(v1, v2, m1, m2):
        """1D elastic collision formula (momentum + kinetic energy conservation)."""
        total = m1 + m2
        new_v1 = (v1 * (m1 - m2) + 2 * m2 * v2) / total
        new_v2 = (v2 * (m2 - m1) + 2 * m1 * v1) / total
        return new_v1, new_v2
