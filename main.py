from engine.physics_engine import PhysicsEngine
from objects.ball import Ball
from utils.vector import Vector

engine = PhysicsEngine()

ball = Ball(
    position=Vector(0, 0),
    velocity=Vector(10, 0),
    mass=1,
    radius=5,
    friction=0.5
)

engine.add_object(ball)
engine.start()

for i in range(10):
    engine.update(0.1)

    print(f"Step {i}")
    print(f"Position: {ball.position}")
    print(f"Velocity: {ball.velocity}")
    print("-----")