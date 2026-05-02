import math
import tkinter as tk
from tkinter import ttk, colorchooser, messagebox

from utils.vector import Vector
from objects.ball import Ball
from objects.block import Block
from database.db_handler import DBHandler

CANVAS_W = 700
CANVAS_H = 600


class SimulatorUI:
    def __init__(self, engine):
        self.engine = engine
        self.db = DBHandler()
        self.selected_color = "#3498db"
        self.selected_index = None      # index into engine.objects, or None

        self.root = tk.Tk()
        self.root.title("Collision Simulation Engine")
        self.root.geometry("1000x700")
        self.root.resizable(False, False)
        self.root.configure(bg="#2e2e2e")

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TCombobox", fieldbackground="#ffffff", background="#ffffff")

        self._create_menu()
        self._create_layout()
        self._create_status_bar()
        self._game_loop()
        self.root.mainloop()

    # ------------------------------------------------------------------ #
    #  Menu
    # ------------------------------------------------------------------ #
    def _create_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save Scenario", command=self._save_scenario)
        file_menu.add_command(label="Load Scenario", command=self._load_scenario)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        sim_menu = tk.Menu(menubar, tearoff=0)
        sim_menu.add_command(label="Start", command=self._start_sim)
        sim_menu.add_command(label="Pause", command=self._pause_sim)
        sim_menu.add_command(label="Reset", command=self._reset_sim)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about)

        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="Simulation", menu=sim_menu)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menubar)

    # ------------------------------------------------------------------ #
    #  Layout
    # ------------------------------------------------------------------ #
    def _create_layout(self):
        main_frame = tk.Frame(self.root, bg="#2e2e2e")
        main_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            main_frame, bg="#ffffff",
            width=CANVAS_W, height=CANVAS_H,
            highlightthickness=0
        )
        self.canvas.pack(side="left")
        self._draw_grid()

        panel_outer = tk.Frame(main_frame, bg="#f4f4f4", width=300)
        panel_outer.pack(side="right", fill="y")
        panel_outer.pack_propagate(False)

        # Scrollable inner panel (handles overflow when many sections are shown)
        scroll_canvas = tk.Canvas(panel_outer, bg="#f4f4f4", highlightthickness=0)
        scrollbar = tk.Scrollbar(panel_outer, orient="vertical",
                                 command=scroll_canvas.yview)
        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        scroll_canvas.pack(side="left", fill="both", expand=True)

        panel = tk.Frame(scroll_canvas, bg="#f4f4f4")
        win_id = scroll_canvas.create_window((0, 0), window=panel, anchor="nw")

        def _on_panel_resize(e):
            scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))

        def _on_canvas_resize(e):
            scroll_canvas.itemconfig(win_id, width=e.width)

        panel.bind("<Configure>", _on_panel_resize)
        scroll_canvas.bind("<Configure>", _on_canvas_resize)

        # Enable mousewheel scrolling
        def _on_mousewheel(e):
            scroll_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        scroll_canvas.bind("<MouseWheel>", _on_mousewheel)
        panel.bind("<MouseWheel>", _on_mousewheel)

        self._create_object_list_section(panel)
        self._create_object_properties_section(panel)
        self._create_simulation_section(panel)
        self._create_speed_slider(panel)
        self._create_scenario_section(panel)

    def _draw_grid(self):
        for x in range(0, CANVAS_W, 20):
            self.canvas.create_line(x, 0, x, CANVAS_H, fill="#e8e8e8")
        for y in range(0, CANVAS_H, 20):
            self.canvas.create_line(0, y, CANVAS_W, y, fill="#e8e8e8")

    # ------------------------------------------------------------------ #
    #  Panel sections
    # ------------------------------------------------------------------ #
    def _create_object_list_section(self, parent):
        frame = tk.LabelFrame(parent, text="Objects in Simulation",
                              fg="#222222", bg="#f4f4f4", font=("Arial", 9, "bold"))
        frame.pack(fill="x", padx=8, pady=(8, 4))

        list_container = tk.Frame(frame, bg="#f4f4f4")
        list_container.pack(fill="x", padx=5, pady=(2, 0))

        sb = tk.Scrollbar(list_container)
        sb.pack(side="right", fill="y")

        self.object_list = tk.Listbox(
            list_container, height=5, font=("Courier", 8),
            yscrollcommand=sb.set, selectmode=tk.SINGLE,
            activestyle="none", bg="#ffffff", relief="solid", bd=1
        )
        self.object_list.pack(side="left", fill="x", expand=True)
        sb.config(command=self.object_list.yview)
        self.object_list.bind("<<ListboxSelect>>", self._on_list_select)

        tk.Button(frame, text="Delete Selected", bg="#c0392b", fg="white",
                  relief="flat", font=("Arial", 8), command=self._delete_selected
                  ).pack(fill="x", padx=5, pady=(3, 5))

    def _create_object_properties_section(self, parent):
        frame = tk.LabelFrame(parent, text="Object Properties",
                              fg="#222222", bg="#f4f4f4", font=("Arial", 9, "bold"))
        frame.pack(fill="x", padx=8, pady=4)
        frame.columnconfigure(1, weight=1)

        # Type row
        tk.Label(frame, text="Type:", bg="#f4f4f4", fg="#444444",
                 font=("Arial", 8), anchor="w"
                 ).grid(row=0, column=0, sticky="w", padx=(6, 2), pady=2)
        self.inp_type = tk.StringVar(value="Ball")
        ttk.Combobox(frame, textvariable=self.inp_type, values=["Ball", "Block"],
                     state="readonly", width=10
                     ).grid(row=0, column=1, sticky="ew", padx=(0, 6), pady=2)

        # Compact grid fields
        fields = [
            ("Pos X",   "0",   "inp_pos_x",  1),
            ("Pos Y",   "0",   "inp_pos_y",  2),
            ("Speed",   "100", "inp_vel_mag", 3),
            ("Angle°",  "45",  "inp_angle",  4),
            ("Mass",    "1",   "inp_mass",   5),
            ("Size",    "20",  "inp_size",   6),
        ]
        for label, default, attr, row in fields:
            tk.Label(frame, text=label + ":", bg="#f4f4f4", fg="#444444",
                     font=("Arial", 8), anchor="w"
                     ).grid(row=row, column=0, sticky="w", padx=(6, 2), pady=1)
            e = tk.Entry(frame, relief="solid", bd=1, width=10, font=("Arial", 8))
            e.insert(0, default)
            e.grid(row=row, column=1, sticky="ew", padx=(0, 6), pady=1)
            setattr(self, attr, e)

        # Color picker
        color_row = tk.Frame(frame, bg="#f4f4f4")
        color_row.grid(row=7, column=0, columnspan=2, sticky="ew", padx=5, pady=3)
        tk.Button(color_row, text="Pick Color", command=self._pick_color,
                  relief="flat", bg="#dddddd", font=("Arial", 8)).pack(side="left")
        self.color_swatch = tk.Label(color_row, bg=self.selected_color,
                                     width=4, relief="solid", bd=1)
        self.color_swatch.pack(side="left", padx=5)

        # Add / Update buttons
        btn_row = tk.Frame(frame, bg="#f4f4f4")
        btn_row.grid(row=8, column=0, columnspan=2, sticky="ew", padx=5, pady=(2, 6))
        tk.Button(btn_row, text="Add New", bg="#27ae60", fg="white",
                  relief="flat", font=("Arial", 8), command=self._add_object
                  ).pack(side="left", fill="x", expand=True, padx=(0, 2))
        tk.Button(btn_row, text="Update Selected", bg="#f39c12", fg="white",
                  relief="flat", font=("Arial", 8), command=self._update_selected
                  ).pack(side="left", fill="x", expand=True, padx=(2, 0))

    def _create_simulation_section(self, parent):
        frame = tk.LabelFrame(parent, text="Simulation",
                              fg="#222222", bg="#f4f4f4", font=("Arial", 9, "bold"))
        frame.pack(fill="x", padx=8, pady=4)
        frame.columnconfigure(1, weight=1)

        # Global friction
        tk.Label(frame, text="Friction:", bg="#f4f4f4", fg="#444444",
                 font=("Arial", 8), anchor="w"
                 ).grid(row=0, column=0, sticky="w", padx=(6, 2), pady=4)
        self.inp_friction = tk.Entry(frame, relief="solid", bd=1,
                                     width=8, font=("Arial", 8))
        self.inp_friction.insert(0, "0.02")
        self.inp_friction.grid(row=0, column=1, sticky="w", padx=(0, 6), pady=4)

        # Control buttons
        btn_row = tk.Frame(frame, bg="#f4f4f4")
        btn_row.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 6))
        tk.Button(btn_row, text="Start", bg="#27ae60", fg="white",
                  relief="flat", font=("Arial", 8), command=self._start_sim
                  ).pack(side="left", fill="x", expand=True, padx=(0, 1))
        tk.Button(btn_row, text="Pause", bg="#f39c12", fg="white",
                  relief="flat", font=("Arial", 8), command=self._pause_sim
                  ).pack(side="left", fill="x", expand=True, padx=1)
        tk.Button(btn_row, text="Reset", bg="#c0392b", fg="white",
                  relief="flat", font=("Arial", 8), command=self._reset_sim
                  ).pack(side="left", fill="x", expand=True, padx=(1, 0))

    def _create_speed_slider(self, parent):
        frame = tk.LabelFrame(parent, text="Speed Control",
                              fg="#222222", bg="#f4f4f4", font=("Arial", 9, "bold"))
        frame.pack(fill="x", padx=8, pady=4)

        self.speed = tk.DoubleVar(value=1.0)
        tk.Scale(frame, from_=0.5, to=2.0, resolution=0.1, orient="horizontal",
                 variable=self.speed, bg="#f4f4f4", highlightthickness=0,
                 font=("Arial", 8)).pack(fill="x", padx=5, pady=2)

    def _create_scenario_section(self, parent):
        frame = tk.LabelFrame(parent, text="Scenarios",
                              fg="#222222", bg="#f4f4f4", font=("Arial", 9, "bold"))
        frame.pack(fill="x", padx=8, pady=(4, 8))

        tk.Label(frame, text="Name:", bg="#f4f4f4", fg="#444444",
                 font=("Arial", 8)).pack(anchor="w", padx=6)
        self.scenario_name = tk.Entry(frame, relief="solid", bd=1, font=("Arial", 8))
        self.scenario_name.pack(fill="x", padx=6, pady=2)

        tk.Button(frame, text="Save", bg="#2c7be5", fg="white",
                  relief="flat", font=("Arial", 8), command=self._save_scenario
                  ).pack(fill="x", padx=5, pady=1)
        tk.Button(frame, text="Load", bg="#6c757d", fg="white",
                  relief="flat", font=("Arial", 8), command=self._load_scenario
                  ).pack(fill="x", padx=5, pady=(1, 6))

    def _create_status_bar(self):
        self.status = tk.Label(
            self.root,
            text="Status: Paused | Objects: 0 | Speed: 1.0x | Friction: 0.02",
            bg="#dcdcdc", fg="#222222", anchor="w", padx=10, font=("Arial", 9)
        )
        self.status.pack(fill="x", side="bottom")

    # ------------------------------------------------------------------ #
    #  Game loop & rendering
    # ------------------------------------------------------------------ #
    def _game_loop(self):
        # Sync global friction from input field every frame
        try:
            self.engine.friction = float(self.inp_friction.get())
        except (ValueError, AttributeError):
            pass

        dt = 0.016 * self.speed.get()
        self.engine.update(dt)
        self._redraw()
        self._update_status()
        self.root.after(16, self._game_loop)

    def _redraw(self):
        self.canvas.delete("object")
        for i, obj in enumerate(self.engine.objects):
            self._draw_object(obj, selected=(i == self.selected_index))

    def _draw_object(self, obj, selected: bool = False):
        cx = obj.position.x + CANVAS_W / 2
        cy = CANVAS_H / 2 - obj.position.y
        outline_color = "#FFD700" if selected else "#555555"
        outline_width = 2 if selected else 1

        if obj.get_shape() == "circle":
            r = obj.radius
            self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill=obj.color, outline=outline_color,
                width=outline_width, tags="object"
            )
        else:
            hw, hh = obj.half_extents
            self.canvas.create_rectangle(
                cx - hw, cy - hh, cx + hw, cy + hh,
                fill=obj.color, outline=outline_color,
                width=outline_width, tags="object"
            )

    def _update_status(self):
        state = "Running" if self.engine.running else "Paused"
        self.status.config(
            text=(f"Status: {state} | Objects: {len(self.engine.objects)} | "
                  f"Speed: {self.speed.get():.1f}x | Friction: {self.engine.friction:.3f}")
        )

    # ------------------------------------------------------------------ #
    #  Object list
    # ------------------------------------------------------------------ #
    def _refresh_object_list(self):
        prev_sel = self.selected_index
        self.object_list.delete(0, tk.END)
        for i, obj in enumerate(self.engine.objects):
            self.object_list.insert(tk.END, self._object_label(obj, i))
        # Restore visual selection
        if prev_sel is not None and prev_sel < len(self.engine.objects):
            self.object_list.selection_set(prev_sel)
            self.object_list.see(prev_sel)
        else:
            self.selected_index = None

    @staticmethod
    def _object_label(obj, i: int) -> str:
        kind = "Ball " if obj.get_shape() == "circle" else "Block"
        size = obj.radius if obj.get_shape() == "circle" else obj.width
        speed = obj.velocity.magnitude()
        return (f"#{i + 1} {kind}  m={obj.mass:<4.1f}  "
                f"r={size:<4.0f}  v={speed:<5.0f}  "
                f"({obj.position.x:5.0f},{obj.position.y:5.0f})")

    def _on_list_select(self, _event):
        sel = self.object_list.curselection()
        if not sel or sel[0] >= len(self.engine.objects):
            self.selected_index = None
            return
        self.selected_index = sel[0]
        self._populate_fields_from_object(self.engine.objects[self.selected_index])

    def _populate_fields_from_object(self, obj):
        self.inp_type.set("Ball" if obj.get_shape() == "circle" else "Block")

        def _set(widget, value):
            widget.delete(0, tk.END)
            widget.insert(0, value)

        _set(self.inp_pos_x,  f"{obj.position.x:.1f}")
        _set(self.inp_pos_y,  f"{obj.position.y:.1f}")

        speed = obj.velocity.magnitude()
        angle = math.degrees(math.atan2(obj.velocity.y, obj.velocity.x)) if speed > 0 else 0
        _set(self.inp_vel_mag, f"{speed:.1f}")
        _set(self.inp_angle,   f"{angle:.1f}")
        _set(self.inp_mass,    f"{obj.mass}")

        size = obj.radius if obj.get_shape() == "circle" else obj.width
        _set(self.inp_size, f"{size:.1f}")

        self.selected_color = obj.color
        self.color_swatch.config(bg=self.selected_color)

    # ------------------------------------------------------------------ #
    #  Object creation / editing
    # ------------------------------------------------------------------ #
    def _build_object_from_fields(self):
        x       = float(self.inp_pos_x.get())
        y       = float(self.inp_pos_y.get())
        vel_mag = float(self.inp_vel_mag.get())
        angle   = math.radians(float(self.inp_angle.get()))
        mass    = float(self.inp_mass.get())
        size    = float(self.inp_size.get())

        if mass <= 0:
            raise ValueError("Mass must be a positive number.")
        if size <= 0:
            raise ValueError("Size must be a positive number.")

        vel = Vector(vel_mag * math.cos(angle), vel_mag * math.sin(angle))
        pos = Vector(x, y)

        if self.inp_type.get() == "Ball":
            return Ball(pos, vel, mass, size, self.selected_color)
        return Block(pos, vel, mass, size, size, self.selected_color)

    def _add_object(self):
        try:
            obj = self._build_object_from_fields()
            self.engine.add_object(obj)
            self._refresh_object_list()
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))

    def _update_selected(self):
        if self.selected_index is None:
            messagebox.showinfo("Update Object", "Select an object from the list first.")
            return
        if self.engine.running:
            messagebox.showwarning("Update Object",
                                   "Pause the simulation before editing objects.")
            return
        try:
            obj = self._build_object_from_fields()
            self.engine.update_object(self.selected_index, obj)
            self._refresh_object_list()
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))

    def _delete_selected(self):
        if self.selected_index is None:
            messagebox.showinfo("Delete Object", "Select an object from the list first.")
            return
        if self.engine.running:
            messagebox.showwarning("Delete Object",
                                   "Pause the simulation before deleting objects.")
            return
        self.engine.remove_object(self.selected_index)
        self.selected_index = None
        self._refresh_object_list()

    def _pick_color(self):
        result = colorchooser.askcolor(color=self.selected_color, title="Pick Color")
        if result[1]:
            self.selected_color = result[1]
            self.color_swatch.config(bg=self.selected_color)

    # ------------------------------------------------------------------ #
    #  Simulation controls
    # ------------------------------------------------------------------ #
    def _start_sim(self):
        self.engine.start()

    def _pause_sim(self):
        self.engine.pause()
        self._refresh_object_list()     # show current positions after stopping

    def _reset_sim(self):
        self.engine.reset()
        self.selected_index = None
        self._refresh_object_list()

    # ------------------------------------------------------------------ #
    #  Scenarios
    # ------------------------------------------------------------------ #
    def _save_scenario(self):
        name = self.scenario_name.get().strip()
        if not name:
            messagebox.showwarning("Save Scenario", "Enter a scenario name first.")
            return
        try:
            friction = float(self.inp_friction.get())
        except ValueError:
            friction = self.engine.friction
        self.db.save_scenario(name, self.engine.initial_objects, friction)
        messagebox.showinfo("Saved", f'Scenario "{name}" saved.')

    def _load_scenario(self):
        names = self.db.list_scenarios()
        if not names:
            messagebox.showinfo("Load Scenario", "No saved scenarios found.")
            return
        self._show_load_dialog(names)

    def _show_load_dialog(self, names: list):
        dialog = tk.Toplevel(self.root)
        dialog.title("Scenarios")
        dialog.resizable(False, False)
        dialog.grab_set()

        tk.Label(dialog, text="Select a scenario:", pady=6,
                 font=("Arial", 9)).pack()

        lb = tk.Listbox(dialog, height=8, width=34, selectmode=tk.SINGLE,
                        font=("Arial", 9))
        for name in names:
            lb.insert(tk.END, name)
        lb.pack(padx=10)

        def on_load():
            sel = lb.curselection()
            if not sel:
                return
            name = lb.get(sel[0])
            objects, friction = self.db.load_scenario(name)
            # clear() wipes both live objects and initial states so add_object
            # can re-register each loaded object as a fresh initial snapshot
            self.engine.clear()
            for obj in objects:
                self.engine.add_object(obj)
            self.engine.friction = friction
            self.inp_friction.delete(0, tk.END)
            self.inp_friction.insert(0, f"{friction:.3f}")
            self.selected_index = None
            self._refresh_object_list()
            dialog.destroy()

        def on_delete():
            sel = lb.curselection()
            if not sel:
                return
            name = lb.get(sel[0])
            if not messagebox.askyesno(
                "Delete Scenario",
                f'Permanently delete "{name}"?',
                parent=dialog
            ):
                return
            self.db.delete_scenario(name)
            lb.delete(sel[0])
            if lb.size() == 0:
                dialog.destroy()   # nothing left to show

        btn_row = tk.Frame(dialog)
        btn_row.pack(pady=8)
        tk.Button(btn_row, text="Load", command=on_load,
                  bg="#2c7be5", fg="white", relief="flat",
                  font=("Arial", 9)).pack(side="left", padx=4)
        tk.Button(btn_row, text="Delete", command=on_delete,
                  bg="#c0392b", fg="white", relief="flat",
                  font=("Arial", 9)).pack(side="left", padx=4)

    # ------------------------------------------------------------------ #
    #  Help
    # ------------------------------------------------------------------ #
    def _show_about(self):
        messagebox.showinfo(
            "About",
            "Collision Simulation Engine\n"
            "CS112 Object-Oriented Programming\n"
            "\n"
            "Team Members\n"
            "─────────────────────────────────────\n"
            "Muhammad Muhib E Ali Naqvi   2025584\n"
            "Jawad Ahmed Khan             2025331\n"
            "Muhammad Ibrahim             2025557\n"
            "Muhammad Abdullah Hassan     2025435\n"
            "─────────────────────────────────────\n"
            "\n"
            "Features\n"
            "• Elastic collisions: Ball-Ball, Ball-Block, Block-Block\n"
            "• Global friction applied uniformly to all objects\n"
            "• Objects stop completely on boundary contact\n"
            "• Select an object in the list to edit or delete it\n"
            "• Reset restores every object to its initial state\n"
            "• Save / Load scenarios (saves the initial configuration)"
        )
