from objects.ball import Ball
from objects.block import Block

from engine.collisions.ball_ball import BallBallCollision
from engine.collisions.ball_block import BallBlockCollision
from engine.collisions.block_block import BlockBlockCollision


class CollisionEngine:
    """
    Central dispatcher for all collision types.
    Each collision type is handled by its own class.
    """

    def __init__(self):
        # Initialize collision handlers (abstraction layer)
        self.ball_ball_collision = BallBallCollision()
        self.ball_block_collision = BallBlockCollision()
        self.block_block_collision = BlockBlockCollision()

    def handle_collisions(self, objects):
        """
        Checks all object pairs and resolves collisions.
        """

        n = len(objects)

        for i in range(n):
            for j in range(i + 1, n):

                a = objects[i]
                b = objects[j]

                # -------------------------
                # BALL - BALL COLLISION
                # -------------------------
                if isinstance(a, Ball) and isinstance(b, Ball):

                    if self.ball_ball_collision.check(a, b):
                        self.ball_ball_collision.resolve(a, b)

                # -------------------------
                # BALL - BLOCK COLLISION
                # -------------------------
                elif isinstance(a, Ball) and isinstance(b, Block):

                    if self.ball_block_collision.check(a, b):
                        self.ball_block_collision.resolve(a, b)

                # -------------------------
                # BLOCK - BALL COLLISION
                # (order flipped, same logic)
                # -------------------------
                elif isinstance(a, Block) and isinstance(b, Ball):

                    if self.ball_block_collision.check(b, a):
                        self.ball_block_collision.resolve(b, a)
                        
                # -------------------------
                # BLOCK - BLOCK COLLISION
                # -------------------------
                elif isinstance(a, Block) and isinstance(b, Block):

                    if self.block_block_collision.check(a, b):
                        self.block_block_collision.resolve(a, b)