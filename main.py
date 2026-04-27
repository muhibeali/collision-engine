from engine.physics_engine import PhysicsEngine
from ui.simulator_ui import SimulatorUI

def main():
    engine = PhysicsEngine()
    engine.start()

    app = SimulatorUI(engine)

if __name__ == "__main__":
    main()