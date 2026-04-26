from engine.physics_engine import PhysicsEngine
from objects.ball import Ball
from objects.block import Block
from utils.vector import Vector
from ui.simulator_ui import SimulatorUI

# ------------------------
# CREATE ENGINE
# ------------------------
engine = PhysicsEngine()

# ------------------------
# BALL (moving toward block diagonally)
# ------------------------
ball = Ball(
    position=Vector(-80, -40),
    velocity=Vector(30, 17.25),
    mass=1,
    radius=10,
    friction=0.02
)

# ------------------------
# BLOCK (static obstacle)
# ------------------------
block = Block(
    position=Vector(40, 0),
    velocity=Vector(0, 0),
    mass=10,
    width=60,
    height=60,
    friction=0
)

engine.add_object(ball)
engine.add_object(block)

# ------------------------
# START SIMULATION
# ------------------------
engine.start()

# ------------------------
# RUN UI (real-time visualization)
# ------------------------
SimulatorUI(engine)