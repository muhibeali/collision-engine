import tkinter as tk
from tkinter import ttk, colorchooser, messagebox

class SimulatorUI:
    def __init__(self, engine):
        self.engine = engine

        self.root = tk.Tk()
        self.root.title("Collision Simulation Engine")
        self.root.geometry("1000x650")
        self.root.resizable(False, False)
        self.root.configure(bg="#e6e6e6")

        self.selected_color = "#3498db"

        style = ttk.Style()
        style.theme_use('default')

        style.configure("TCombobox",
            fieldbackground="#ffffff",
            background="#ffffff"
        )

        self.create_menu()
        self.create_layout()
        self.create_status_bar()

        self.objects = []
        self.game_loop()
        self.root.mainloop()

    # ---------------- MENU ---------------- #
    def create_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save Scenario", command=self.save_scenario)
        file_menu.add_command(label="Load Scenario", command=self.load_scenario)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        sim_menu = tk.Menu(menubar, tearoff=0)
        sim_menu.add_command(label="Start", command=self.start_sim)
        sim_menu.add_command(label="Pause", command=self.pause_sim)
        sim_menu.add_command(label="Reset", command=self.reset_sim)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)

        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="Simulation", menu=sim_menu)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    # ---------------- LAYOUT ---------------- #
    def create_layout(self):
        main_frame = tk.Frame(self.root, bg="#2e2e2e")
        main_frame.pack(fill="both", expand=True)

        # LEFT: CANVAS
        self.canvas = tk.Canvas(
            main_frame,
            bg="#ffffff",
            width=700,
            height=600,
            highlightthickness=0
        )
        self.canvas.pack(side="left", fill="both", expand=True)

        self.draw_grid()

        # RIGHT: CONTROL PANEL
        panel = tk.Frame(main_frame, bg="#f4f4f4", width=300)
        panel.pack(side="right", fill="y")

        self.create_object_section(panel)
        self.create_control_buttons(panel)
        self.create_speed_slider(panel)
        self.create_scenario_section(panel)

    # ---------------- GRID ---------------- #
    def draw_grid(self):
        for i in range(0, 700, 20):
            self.canvas.create_line(i, 0, i, 600, fill="#d0d0d0")
        for i in range(0, 600, 20):
            self.canvas.create_line(0, i, 700, i, fill="#d0d0d0")

    # ---------------- OBJECT INPUT ---------------- #
    def create_object_section(self, parent):
        frame = tk.LabelFrame(parent, text="Add Object", fg="#222222", bg="#f4f4f4")
        frame.pack(fill="x", padx=10, pady=10)

        self.type_var = tk.StringVar(value="Ball")
        ttk.Combobox(frame, textvariable=self.type_var, values=["Ball", "Block"]).pack(pady=5)

        self.entry(frame, "Position X", "0")
        self.entry(frame, "Position Y", "0")

        self.entry(frame, "Velocity Magnitude", "50")
        self.entry(frame, "Angle (deg)", "45")

        self.entry(frame, "Mass", "1")
        self.entry(frame, "Size (r / w)", "20")

        self.entry(frame, "Friction", "0.02")

        tk.Button(frame, text="Pick Color", command=self.pick_color).pack(pady=5)

        tk.Button(frame, text="Add Object", bg="#2c7be5", fg="white", relief="flat",
                  command=self.add_object).pack(pady=5)

    def entry(self, parent, label, default):
        tk.Label(parent, text=label, fg="#222222", bg="#f4f4f4").pack()
        e = tk.Entry(parent)
        e.insert(0, default)
        e.pack()
        key = label.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")
        setattr(self, key, e)

    # ---------------- CONTROLS ---------------- #
    def create_control_buttons(self, parent):
        frame = tk.LabelFrame(parent, text="Simulation Controls", fg="#222222", bg="#f4f4f4")
        frame.pack(fill="x", padx=10, pady=10)

        tk.Button(frame, text="Start", bg="#27ae60", fg="white",
                  command=self.start_sim).pack(fill="x", pady=2)

        tk.Button(frame, text="Pause", bg="#f39c12", fg="white",
                  command=self.pause_sim).pack(fill="x", pady=2)

        tk.Button(frame, text="Reset", bg="#c0392b", fg="white",
                  command=self.reset_sim).pack(fill="x", pady=2)

    # ---------------- SPEED ---------------- #
    def create_speed_slider(self, parent):
        frame = tk.LabelFrame(parent, text="Speed Control", fg="#222222", bg="#f4f4f4")
        frame.pack(fill="x", padx=10, pady=10)

        self.speed = tk.DoubleVar(value=1.0)

        tk.Scale(frame, from_=0.5, to=2.0, resolution=0.1,
                 orient="horizontal", variable=self.speed).pack(fill="x")

    # ---------------- SCENARIO ---------------- #
    def create_scenario_section(self, parent):
        frame = tk.LabelFrame(parent, text="Scenarios", fg="#222222", bg="#f4f4f4")
        frame.pack(fill="x", padx=10, pady=10)

        self.scenario_name = tk.Entry(frame)
        self.scenario_name.pack(pady=5)

        tk.Button(frame, text="Save", command=self.save_scenario).pack(fill="x")
        tk.Button(frame, text="Load", command=self.load_scenario).pack(fill="x")

    # ---------------- STATUS ---------------- #
    def create_status_bar(self):
        self.status = tk.Label(
            self.root,
            text="Status: Ready | Objects: 0 | Speed: 1.0x",
            bg="#dcdcdc",
            fg="#222222",
            anchor="w",
            padx=10
        )
        self.status.pack(fill="x")

    # ---------------- ACTIONS (PLACEHOLDER) ---------------- #
    def add_object(self):

        from utils.vector import Vector
        import math

        try:
            obj_type = self.type_var.get()

            x = float(self.position_x.get())
            y = float(self.position_y.get())

            magnitude = float(self.velocity_magnitude.get())
            angle = float(self.angle_deg.get())

            mass = float(self.mass.get())
            size = float(self.size_r___w.get())
            friction = float(self.friction.get())

            # Convert angle → radians
            angle_rad = math.radians(angle)

            vx = magnitude * math.cos(angle_rad)
            vy = magnitude * math.sin(angle_rad)

            velocity = Vector(vx, vy)
            position = Vector(x, y)

            if obj_type == "Ball":
                from objects.ball import Ball

                obj = Ball(
                    position=position,
                    velocity=velocity,
                    mass=mass,
                    radius=size,
                    friction=friction
                )

            else:
                from objects.block import Block

                obj = Block(
                    position=position,
                    velocity=velocity,
                    mass=mass,
                    width=size,
                    height=size,
                    friction=friction
                )

            # Add to engine
            self.engine.add_object(obj)

            # Draw object
            self.draw_object(obj)

            self.status.config(text=f"Added {obj_type}")

        except Exception as e:
            self.status.config(text=f"Error: {str(e)}")

    def draw_object(self, obj):

        scale = 1  # you can change later

        x = obj.position.x + 350
        y = 300 - obj.position.y

        color = self.selected_color

        if hasattr(obj, "radius"):  # Ball
            r = obj.radius

            self.canvas.create_oval(
                x - r, y - r,
                x + r, y + r,
                fill=color,
                outline="",
                tags="object"
            )

        else:  # Block
            w = obj.width / 2
            h = obj.height / 2

            self.canvas.create_rectangle(
                x - w, y - h,
                x + w, y + h,
                fill=color,
                outline="",
                tags="object"
            )

    def game_loop(self):

        dt = 0.016 * self.speed.get()  # ~60 FPS scaled

        self.engine.update(dt)

        self.redraw()

        self.root.after(16, self.game_loop)
    
    def redraw(self):

        self.canvas.delete("object")

        for obj in self.engine.objects:
            self.draw_object(obj)

    def start_sim(self):
        self.status.config(text="Status: Running")
        print("Simulation Started")

    def pause_sim(self):
        self.status.config(text="Status: Paused")
        print("Simulation Paused")

    def reset_sim(self):
        self.status.config(text="Status: Reset")
        print("Simulation Reset")

    def save_scenario(self):
        print("Save Scenario")

    def load_scenario(self):
        print("Load Scenario")

    def show_about(self):
        messagebox.showinfo("About", "Collision Simulation Engine\nCS112 Project")

    def pick_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.selected_color = color