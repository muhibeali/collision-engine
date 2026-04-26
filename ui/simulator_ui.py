import tkinter as tk
from engine.physics_engine import PhysicsEngine
from objects.ball import Ball
from objects.block import Block
from utils.vector import Vector

class SimulatorUI:
    def __init__(self, engine):
        self.engine = engine

        self.root = tk.Tk()
        self.root.title("Collision Simulation Engine")

        self.width = 600
        self.height = 600

        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="white")
        self.canvas.pack()

        # Convert physics coords to screen center
        self.offset_x = self.width / 2
        self.offset_y = self.height / 2

        self.running = True

        self.loop()

        self.root.mainloop()

    def to_screen(self, pos):
        return (
            pos.x + self.offset_x,
            self.offset_y - pos.y
        )

    def draw(self):
        self.canvas.delete("all")

        for obj in self.engine.objects:

            if isinstance(obj, Ball):
                x, y = self.to_screen(obj.position)
                r = obj.radius

                self.canvas.create_oval(
                    x - r, y - r,
                    x + r, y + r,
                    fill="blue"
                )

            elif isinstance(obj, Block):
                x, y = self.to_screen(obj.position)
                w = obj.width / 2
                h = obj.height / 2

                self.canvas.create_rectangle(
                    x - w, y - h,
                    x + w, y + h,
                    fill="red"
                )

    def loop(self):
        if self.running:
            self.engine.update(0.1)
            self.draw()

        self.root.after(16, self.loop)  # ~60 FPS