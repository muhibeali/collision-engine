from objects.ball import Ball
from objects.block import Block
from engine.collisions.ball_ball import BallBallCollision
from engine.collisions.ball_block import BallBlockCollision
from engine.collisions.block_block import BlockBlockCollision


class CollisionEngine:
    def __init__(self):
        self._handlers = {
            (Ball, Ball): BallBallCollision(),
            (Ball, Block): BallBlockCollision(),
            (Block, Block): BlockBlockCollision(),
        }

    def handle_collisions(self, objects):
        n = len(objects)
        for i in range(n):
            for j in range(i + 1, n):
                self._dispatch(objects[i], objects[j])

    def _dispatch(self, a, b):
        key = (type(a), type(b))
        handler = self._handlers.get(key)
        if handler is None:
            # Try reversed order (e.g. Block→Ball becomes Ball→Block)
            key = (type(b), type(a))
            handler = self._handlers.get(key)
            if handler is None:
                return
            a, b = b, a

        if handler.check(a, b):
            handler.resolve(a, b)
