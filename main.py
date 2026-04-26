from engine.physics_engine import PhysicsEngine
from objects.ball import Ball
from objects.block import Block
from utils.vector import Vector
from ui.simulator_ui import SimulatorUI

# ------------------------
# CREATE PHYSICS ENGINE
# ------------------------
engine = PhysicsEngine()

# ------------------------
# ADD OBJECTS
# ------------------------

# Moving ball
ball = Ball(
    position=Vector(-80, 0),
    velocity = Vector(20, 10),
    mass=1,
    radius=10,
    friction=0.05
)

# Static block
block = Block(
    position=Vector(60, 0),
    velocity=Vector(0, 0),
    mass=10,
    width=40,
    height=40,
    friction=0
)

engine.add_object(ball)
engine.add_object(block)

# ------------------------
# START SIMULATION
# ------------------------
engine.start()

# ------------------------
# START UI (this runs the loop)
# ------------------------
SimulatorUI(engine)