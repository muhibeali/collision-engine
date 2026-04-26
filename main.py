from engine.physics_engine import PhysicsEngine
from objects.ball import Ball
from utils.vector import Vector

engine = PhysicsEngine()

ball1 = Ball(Vector(0, 0), Vector(10, 0), mass=1, radius=5, friction=0)
ball2 = Ball(Vector(15, 0), Vector(-5, 0), mass=1, radius=5, friction=0)

engine.add_object(ball1)
engine.add_object(ball2)
engine.start()

for i in range(10):
    engine.update(0.1)

    print(f"Step {i}")
    print("Ball1:", ball1.position, ball1.velocity)
    print("Ball2:", ball2.position, ball2.velocity)
    print("-----")