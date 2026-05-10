# Collision Simulation Engine (2D)

**CS112 – Object-Oriented Programming**

A 2D physics-based simulation built in Python that models the motion and elastic collisions of objects (balls and blocks) inside a bounded environment. The project demonstrates OOP principles, physics modelling, GUI development, and database-backed persistence.

---

## Team Members

| Name | Registration |
|------|-------------|
| Muhammad Muhib E Ali Naqvi | 2025584 |
| Jawad Ahmed Khan | 2025331 |
| Muhammad Ibrahim | 2025557 |
| Muhammad Abdullah Hassan | 2025435 |

---

## How to Run

```
python main.py
```

Python 3 and Tkinter (included in the standard library) are the only requirements.

---

## Project Structure

```
collision_engine/
│
├── main.py                          Entry point
│
├── engine/                          Physics layer
│   ├── physics_engine.py            Master simulation loop + boundary logic
│   ├── collision_engine.py          Collision dispatcher
│   └── collisions/
│       ├── base_collision.py        Abstract base for all collision handlers
│       ├── ball_ball.py             Ball ↔ Ball elastic collision
│       ├── ball_block.py            Ball ↔ Block elastic collision
│       └── block_block.py          Block ↔ Block elastic collision
│
├── objects/                         Physical object hierarchy
│   ├── base_object.py               Abstract base class for all objects
│   ├── ball.py                      Circle-shaped object
│   └── block.py                     Rectangle-shaped object
│
├── utils/
│   └── vector.py                    2D vector math
│
├── database/
│   └── db_handler.py                SQLite scenario save / load / delete
│
├── ui/
│   └── simulator_ui.py              Tkinter GUI (all panels, rendering, controls)
│
└── simulation.db                    SQLite database (created on first run)
```

---

## Physics Model

### Coordinate System

The canvas is 700 × 600 pixels. Physics coordinates are centred on the canvas:

```
Physics (0, 0)  →  Canvas centre (350, 300)
Physics X range →  −350 (left edge) to +350 (right edge)
Physics Y range →  −300 (bottom edge) to +300 (top edge)

Conversion:
  canvas_x = physics_x + 350
  canvas_y = 300 − physics_y   (screen Y is flipped)
```

Positive Y is *up* in physics space, negative Y is *down*.

### Motion

Each frame the engine calls `obj.update(dt)` which moves the object:

```
position += velocity × dt
```

`dt` is 0.016 seconds (≈ 60 FPS) multiplied by the speed slider value (0.5 – 2.0).

### Friction

A single global friction coefficient (default `0.02`) is applied to every object each frame before it moves:

```
decay  = max(0, 1 − friction × dt)
velocity *= decay
```

If the resulting speed falls below 0.01 the velocity is zeroed to prevent infinite sliding.

### Boundary Behaviour

When any part of an object crosses a wall the engine clamps its position to the wall surface and **zeroes the full velocity** – the object stops completely rather than sliding along the edge.

### Elastic Collisions

All collisions conserve both **momentum** and **kinetic energy** (perfectly elastic). The impulse-based formulas are detailed in the collision-handler descriptions below.

---

## File-by-File Reference

---

### `main.py`

The application entry point. Creates a `PhysicsEngine` instance and passes it to `SimulatorUI`, which takes over the event loop.

```python
def main():
    engine = PhysicsEngine()
    SimulatorUI(engine)
```

---

### `utils/vector.py` — `Vector`

A 2D vector class used everywhere for positions and velocities. All arithmetic operators return **new** `Vector` instances (immutable style).

| Method / Operator | Description |
|---|---|
| `Vector(x, y)` | Create a vector. `x` and `y` are stored as `float`. |
| `v1 + v2` | Component-wise addition. Returns new `Vector`. |
| `v1 - v2` | Component-wise subtraction. Returns new `Vector`. |
| `v * scalar` | Scalar multiplication. Returns new `Vector`. |
| `v / scalar` | Scalar division. Returns new `Vector`. |
| `-v` | Negation. Returns new `Vector`. |
| `v.magnitude()` | Euclidean length: `sqrt(x² + y²)`. |
| `v.normalize()` | Unit vector in same direction. Returns zero vector if magnitude is 0. |
| `v.dot(other)` | Dot product: `x·ox + y·oy`. |
| `v.distance_to(other)` | Euclidean distance between two points. Equivalent to `(v - other).magnitude()`. |
| `repr(v)` | `"Vector(x.xx, y.yy)"` |

---

### `objects/base_object.py` — `BaseObject` (Abstract)

Abstract base class that every physical object must inherit. Enforces a consistent interface used by the physics engine and collision system.

```
BaseObject
├── position  : Vector   current world position (physics coords)
├── velocity  : Vector   current velocity (units/second)
├── mass      : float    inertial mass (kg equivalent)
└── color     : str      hex colour string used by the renderer
```

**Abstract members** — every subclass must implement:

| Member | Type | Description |
|---|---|---|
| `half_extents` | `@property` | Returns `(half_width, half_height)` as a tuple. Used by the boundary handler and rectangle renderer so the engine never needs to know the concrete type. |
| `update(dt)` | method | Advance position by one time step. |
| `get_shape()` | method | Returns `"circle"` or `"rectangle"`. Used by the renderer to decide which canvas primitive to draw. |

---

### `objects/ball.py` — `Ball`

A circle-shaped object. Inherits `BaseObject`.

**Constructor:** `Ball(position, velocity, mass, radius, color="#3498db")`

| Attribute | Description |
|---|---|
| `radius` | Circle radius in physics units (= pixels at 1:1 scale). |
| `half_extents` | Returns `(radius, radius)`. A ball's bounding box is a square with side `2 × radius`. |
| `update(dt)` | `position += velocity × dt` |
| `get_shape()` | Returns `"circle"` |

---

### `objects/block.py` — `Block`

An axis-aligned rectangle-shaped object. Inherits `BaseObject`.

**Constructor:** `Block(position, velocity, mass, width, height, color="#e74c3c")`

The position is the **centre** of the rectangle.

| Attribute | Description |
|---|---|
| `width` / `height` | Full dimensions in physics units. |
| `half_extents` | Returns `(width/2, height/2)`. |
| `update(dt)` | `position += velocity × dt` |
| `get_shape()` | Returns `"rectangle"` |

---

### `engine/collisions/base_collision.py` — `BaseCollision` (Abstract)

Defines the two-phase interface every collision handler must implement.

| Method | Signature | Description |
|---|---|---|
| `check` | `(a, b) → bool` | Return `True` if the two objects are currently overlapping (collision detected). |
| `resolve` | `(a, b) → None` | Apply impulse forces and positional corrections to separate the objects and update their velocities. |

---

### `engine/collisions/ball_ball.py` — `BallBallCollision`

Handles collisions between two `Ball` objects.

**`check(a, b)`**

Returns `True` when the distance between centres is less than or equal to the sum of radii:
```
distance(a.position, b.position) ≤ a.radius + b.radius
```

**`resolve(a, b)`**

1. Compute the collision normal `n̂` (unit vector from `a` to `b`).
2. Compute the relative velocity along the normal:
   ```
   vel_along = (a.velocity − b.velocity) · n̂
   ```
   If `vel_along ≤ 0` the balls are already separating — skip.
3. Compute the scalar impulse `j` using the elastic collision formula:
   ```
   j = (2 × vel_along) / (1/a.mass + 1/b.mass)
   ```
4. Apply impulse to both objects:
   ```
   a.velocity −= n̂ × (j / a.mass)
   b.velocity += n̂ × (j / b.mass)
   ```
5. Positional correction — push overlapping balls apart by half the overlap distance each so they no longer intersect.

---

### `engine/collisions/ball_block.py` — `BallBlockCollision`

Handles collisions between a `Ball` and a `Block`.

**`_closest_point(ball, block)`** *(private helper)*

Finds the point on the block's surface (or interior) closest to the ball's centre using axis-aligned clamping:
```
closest_x = clamp(ball.x,  block.left,  block.right)
closest_y = clamp(ball.y,  block.bottom, block.top)
```

**`check(ball, block)`**

Returns `True` when the distance from the ball centre to the closest point on the block is less than or equal to the ball's radius.

**`resolve(ball, block)`**

1. Compute the outward normal `n̂` pointing from the closest surface point toward the ball centre. If the ball centre is exactly on the closest point (centre inside block) the fallback direction `(1, 0)` is used.
2. Compute relative velocity along the normal:
   ```
   vel_along = (ball.velocity − block.velocity) · n̂
   ```
   If `vel_along ≥ 0` they are separating — skip.
3. Compute impulse magnitude:
   ```
   j = (−2 × vel_along) / (1/ball.mass + 1/block.mass)
   ```
4. Apply impulse:
   ```
   ball.velocity  += n̂ × (j / ball.mass)
   block.velocity −= n̂ × (j / block.mass)
   ```
   The block gains momentum — it moves when hit.
5. Positional correction — push the ball out of the block proportionally to each object's mass share.

---

### `engine/collisions/block_block.py` — `BlockBlockCollision`

Handles collisions between two `Block` objects (axis-aligned rectangles).

**`check(a, b)`**

AABB overlap test: two rectangles overlap when their centre-to-centre distances on *both* axes are smaller than the sum of their half-extents:
```
|a.x − b.x| < (a.width  + b.width)  / 2  AND
|a.y − b.y| < (a.height + b.height) / 2
```

**`resolve(a, b)`**

1. Compute the penetration depth on both the X and Y axes.
2. Select the axis with the **smaller** penetration (minimum translation vector). This is the collision axis.
3. Check if the objects are already separating along that axis — if so, skip.
4. Push each block half the overlap distance apart along the chosen axis.
5. Exchange velocities along that axis using the **1D elastic collision formula**:

**`_elastic_1d(v1, v2, m1, m2)`** *(static helper)*

Standard 1D elastic collision result — conserves momentum and kinetic energy:
```
new_v1 = (v1(m1 − m2) + 2·m2·v2) / (m1 + m2)
new_v2 = (v2(m2 − m1) + 2·m1·v1) / (m1 + m2)
```

---

### `engine/collision_engine.py` — `CollisionEngine`

Iterates all object pairs each frame and dispatches to the correct collision handler.

**Internal handler table**

```python
{
    (Ball,  Ball):  BallBallCollision(),
    (Ball,  Block): BallBlockCollision(),
    (Block, Block): BlockBlockCollision(),
}
```

| Method | Description |
|---|---|
| `handle_collisions(objects)` | O(n²) loop over all unique pairs `(i, j)` where `j > i`. Calls `_dispatch` for each pair. |
| `_dispatch(a, b)` | Looks up the handler by `(type(a), type(b))`. If not found, tries the reversed key `(type(b), type(a))` and swaps arguments so the handler always receives objects in the expected order. Calls `handler.check()` then `handler.resolve()` if overlapping. |

---

### `engine/physics_engine.py` — `PhysicsEngine`

The central simulation controller. Owns the object list, friction setting, and boundary constants. All simulation state lives here.

```
BOUNDS = { left: −350, right: 350, bottom: −300, top: 300 }
```

**State**

| Attribute | Type | Description |
|---|---|---|
| `objects` | `list` | Live simulation objects (move every frame). |
| `initial_objects` | `list` | Deep-copy snapshots of each object at the moment it was added or last edited. Used for `reset()` and `save_scenario()`. |
| `running` | `bool` | Whether the simulation is advancing. |
| `friction` | `float` | Global friction coefficient (default `0.02`). Shared by all objects. |
| `collision_engine` | `CollisionEngine` | Handles all object-to-object collision detection and resolution. |

**Object management**

| Method | Description |
|---|---|
| `add_object(obj)` | Appends `obj` to `objects` and stores a `deepcopy` in `initial_objects`. |
| `update_object(index, obj)` | Replaces `objects[index]` with `obj` and updates `initial_objects[index]` with a fresh deep copy. Used by the UI's "Update Selected" flow. |
| `remove_object(index)` | Deletes the object at `index` from both `objects` and `initial_objects`. |

**Lifecycle**

| Method | Description |
|---|---|
| `start()` | Sets `running = True`. |
| `pause()` | Sets `running = False`. |
| `reset()` | Restores `objects` from `initial_objects` (deep copies) and sets `running = False`. Every object returns to its original position and velocity. |
| `clear()` | Empties both `objects` and `initial_objects` and stops the simulation. Called before loading a saved scenario. |

**Per-frame pipeline** (`update(dt)`)

1. **Friction** — `_apply_friction(obj, dt)` applied to every object before movement.
2. **Movement** — `obj.update(dt)` moves each object by its velocity.
3. **Collisions** — `collision_engine.handle_collisions(objects)` resolves all object-to-object overlaps.
4. **Boundaries** — `_handle_boundaries(obj)` clamps positions and stops objects at walls.

**`_apply_friction(obj, dt)`**

```
decay = max(0, 1 − engine.friction × dt)
obj.velocity *= decay
if speed < 0.01 → velocity = (0, 0)
```

**`_handle_boundaries(obj)`**

Checks all four walls using `obj.half_extents` (no `isinstance` needed). If any wall is touched, the position is clamped and the **entire velocity is zeroed** — objects stop dead at boundaries rather than sliding along them.

---

### `database/db_handler.py` — `DBHandler`

Provides SQLite-backed persistence for simulation scenarios. The database file (`simulation.db`) is created automatically on first run.

#### Schema

```
┌─────────────────────────────┐
│         scenarios           │
├──────┬────────┬─────────────┤
│  id  │  name  │  friction   │
│  INT │  TEXT  │  REAL 0.02  │
│  PK  │UNIQUE  │             │
└──────┴────────┴─────────────┘
         │ 1
         │
         │ N (ON DELETE CASCADE)
         ▼
┌────────────────────────────────────────────────────────┐
│                        objects                         │
├────┬─────────────┬──────┬──────┬──────┬───┬───────────┤
│ id │ scenario_id │ type │pos_x │pos_y │…  │radius/w/h │
│INT │     INT FK  │TEXT  │REAL  │REAL  │   │REAL       │
└────┴─────────────┴──────┴──────┴──────┴───┴───────────┘
```

- **`scenarios`** — one row per named scenario. Stores the global friction value.
- **`objects`** — one row per object. `type` is `"ball"` or `"block"`. Ball rows use `radius`; block rows use `width` and `height`. Deleting a scenario row **cascades** to delete all its objects automatically.

> **Important:** scenarios always store the **initial state** of objects (positions and velocities when objects were first added or last edited), not the state at the time of saving. This means loading a scenario always reproduces the original setup from scratch.

**Methods**

| Method | Description |
|---|---|
| `__init__(path="simulation.db")` | Opens (or creates) the database and runs `_init_db()`. |
| `_init_db()` | Creates the `scenarios` and `objects` tables if they do not exist. Also runs a migration to add the `friction` column to any database created before that column existed. |
| `save_scenario(name, objects, friction)` | Upserts the scenario row (INSERT OR REPLACE). Deletes and re-inserts all object rows so the save is idempotent. Accepts `engine.initial_objects`, not the live objects list. |
| `load_scenario(name)` | Returns `(list[BaseObject], friction: float)`. Reconstructs `Ball` and `Block` instances from the stored rows. Returns `([], 0.02)` if the name is not found. |
| `list_scenarios()` | Returns a `list[str]` of all saved scenario names sorted alphabetically. |
| `delete_scenario(name)` | Deletes the scenario row. The `ON DELETE CASCADE` foreign key removes all its object rows automatically. |

---

### `ui/simulator_ui.py` — `SimulatorUI`

The entire graphical interface. Built with Tkinter. Runs at approximately 60 FPS using `root.after(16, ...)`.

#### Window Layout

```
┌──────────────────────────────────────────────┬──────────────┐
│                                              │  Right Panel │
│              Canvas  700 × 600               │   300 px     │
│         (white grid background)              │  (scrollable)│
│                                              │              │
└──────────────────────────────────────────────┴──────────────┘
│  Status bar                                                  │
└──────────────────────────────────────────────────────────────┘
```

The right panel is scrollable — a Tkinter `Canvas` widget with a frame embedded inside it, allowing the panel to be taller than the visible area and scrolled with the mouse wheel.

#### Coordinate Mapping (Physics → Canvas)

```python
canvas_x = obj.position.x + 350    # shift origin from canvas-left to centre
canvas_y = 300 − obj.position.y    # flip Y axis (screen Y grows downward)
```

#### Menu Bar

| Menu | Item | Action |
|---|---|---|
| File | Save Scenario | Calls `_save_scenario()` |
| File | Load Scenario | Calls `_load_scenario()` |
| File | Exit | Closes the window |
| Simulation | Start | Calls `_start_sim()` |
| Simulation | Pause | Calls `_pause_sim()` |
| Simulation | Reset | Calls `_reset_sim()` |
| Help | About | Shows team info and feature list |

#### Right Panel Sections

**Objects in Simulation**

A scrollable `Listbox` showing every object currently in the engine. Each entry shows:
```
#1 Ball   m=1.0   r=20    v=100    (   0,   0)
```
(index, type, mass, size/radius, speed, position)

- Clicking an entry populates the "Object Properties" fields with that object's current values.
- The selected object is highlighted with a gold border on the canvas.
- "Delete Selected" removes the object (requires simulation to be paused).

**Object Properties**

A form for configuring and creating or editing objects.

| Field | Description |
|---|---|
| Type | Dropdown — `Ball` or `Block`. |
| Pos X / Pos Y | Initial position in physics coordinates. Centre of canvas is (0, 0). |
| Speed | Velocity magnitude in units per second. |
| Angle° | Direction of velocity in degrees. 0° = right, 90° = up, 180° = left, etc. |
| Mass | Object mass. Heavier objects transfer less velocity on collision. |
| Size | Radius for balls; side length (width = height) for blocks. |
| Pick Color | Opens the system colour picker. A coloured swatch shows the current choice. |

Buttons:
- **Add New** — builds an object from the form fields and calls `engine.add_object()`.
- **Update Selected** — replaces the selected object in-place (both live and initial states). Requires simulation to be paused.

**Simulation**

| Control | Description |
|---|---|
| Friction | Global friction entry field. Synced to `engine.friction` on every frame so changes take effect immediately. |
| Start | `engine.start()` — begins or resumes physics updates. |
| Pause | `engine.pause()` + refreshes the object list to show current positions. |
| Reset | `engine.reset()` — restores all objects to their initial positions and velocities, clears selection. |

**Speed Control**

A horizontal slider (0.5× – 2.0×, step 0.1). The `dt` passed to `engine.update()` is scaled by this value, making the entire simulation faster or slower.

**Scenarios**

| Control | Description |
|---|---|
| Name entry | Text field for the scenario name. |
| Save | Calls `db.save_scenario()` with `engine.initial_objects` and the current friction value. Overwrites if the name already exists. |
| Load | Opens the scenario browser dialog. |

The **scenario browser dialog** is a modal `Toplevel` window showing all saved scenarios:
- **Load** — calls `engine.clear()` then re-adds each loaded object via `engine.add_object()`, sets friction, closes the dialog.
- **Delete** — asks for confirmation, calls `db.delete_scenario()`, removes the entry from the listbox. If the last scenario is deleted the dialog closes automatically.

#### Internal Methods

**Rendering pipeline**

| Method | Description |
|---|---|
| `_game_loop()` | Called every 16 ms. Syncs friction from the entry field, calls `engine.update(dt)`, redraws, updates the status bar, re-schedules itself. |
| `_redraw()` | Deletes all canvas items tagged `"object"` and redraws every object. The grid is not tagged so it is never erased. |
| `_draw_object(obj, selected)` | Draws a single object. Circles use `create_oval`; rectangles use `create_rectangle`. Selected objects get a gold outline (2 px wide); others get a grey outline (1 px). |
| `_update_status()` | Updates the status bar label with the current running state, object count, speed multiplier, and friction value. |
| `_draw_grid()` | Draws light grey lines every 20 pixels in both directions on the canvas. Called once at startup. |

**Object list management**

| Method | Description |
|---|---|
| `_refresh_object_list()` | Rebuilds the listbox from `engine.objects`. Restores the visual selection if the previously selected index is still valid. |
| `_object_label(obj, i)` | Static helper — returns the formatted string for one listbox row. |
| `_on_list_select(event)` | Listbox `<<ListboxSelect>>` handler. Sets `selected_index` and calls `_populate_fields_from_object()`. |
| `_populate_fields_from_object(obj)` | Fills the Object Properties form from the given object's attributes. Converts velocity back to (magnitude, angle) form. Updates the colour swatch. |

**Object creation / editing**

| Method | Description |
|---|---|
| `_build_object_from_fields()` | Reads all Object Properties entry fields, validates mass > 0 and size > 0, converts (speed, angle) to a velocity `Vector`, and constructs and returns a `Ball` or `Block`. Raises `ValueError` on bad input. |
| `_add_object()` | Calls `_build_object_from_fields()`, then `engine.add_object()`, then refreshes the list. Shows an error dialog on `ValueError`. |
| `_update_selected()` | Guards: selection must exist, simulation must be paused. Calls `_build_object_from_fields()` and `engine.update_object()`. |
| `_delete_selected()` | Guards: selection must exist, simulation must be paused. Calls `engine.remove_object()`. |
| `_pick_color()` | Opens the system colour chooser. Updates `selected_color` and the colour swatch label. |

**Simulation controls**

| Method | Description |
|---|---|
| `_start_sim()` | `engine.start()` |
| `_pause_sim()` | `engine.pause()` + `_refresh_object_list()` |
| `_reset_sim()` | `engine.reset()`, clears `selected_index`, `_refresh_object_list()` |

**Scenario I/O**

| Method | Description |
|---|---|
| `_save_scenario()` | Validates the name field is not empty, reads friction, calls `db.save_scenario(name, engine.initial_objects, friction)`. |
| `_load_scenario()` | Fetches scenario names from `db.list_scenarios()`. Shows a message if none exist, otherwise calls `_show_load_dialog()`. |
| `_show_load_dialog(names)` | Creates the modal browser. See Right Panel — Scenarios above. |

---

## OOP Design Patterns Used

| Pattern | Where |
|---|---|
| **Abstract Base Class** | `BaseObject` (objects), `BaseCollision` (handlers) — enforce a shared interface using Python's `abc.ABC` and `@abstractmethod`. |
| **Template Method** | `PhysicsEngine.update()` defines the fixed pipeline (friction → move → collide → boundary) while the per-step details are in private helpers. |
| **Strategy** | `CollisionEngine` selects the correct `BaseCollision` handler at runtime based on object types, stored in a `dict` keyed by `(type_a, type_b)`. New collision types can be added by inserting a new key — no existing code changes. |
| **Encapsulation** | `PhysicsEngine` owns and manages both `objects` and `initial_objects`. Outside code uses `add_object`, `update_object`, `remove_object` rather than mutating the lists directly. |
| **Separation of concerns** | Physics (`engine/`), data (`objects/`), persistence (`database/`), math (`utils/`), and presentation (`ui/`) are completely independent layers. |

---

## Data Flow Summary

```
User fills form → _add_object()
                       │
                       ▼
              _build_object_from_fields()
                 constructs Ball / Block
                       │
                       ▼
              engine.add_object(obj)
               objects.append(obj)
               initial_objects.append(deepcopy(obj))

                  ┌───────────────────────────────────┐
User clicks       │          _game_loop() (16 ms)      │
  Start    ──────►│  engine.friction ← inp_friction    │
                  │  engine.update(dt)                 │
                  │    ├─ _apply_friction(obj, dt)     │
                  │    ├─ obj.update(dt)               │
                  │    ├─ collision_engine             │
                  │    │    .handle_collisions()       │
                  │    └─ _handle_boundaries(obj)      │
                  │  _redraw()                         │
                  │  _update_status()                  │
                  └───────────────────────────────────┘

User clicks Pause → engine.pause()
                     _refresh_object_list()   ← shows current positions

User clicks Reset → engine.reset()
                     objects ← deepcopy(initial_objects)
                     _refresh_object_list()   ← shows initial positions

User clicks Save  → db.save_scenario(name, engine.initial_objects, friction)
                     stores initial state, not current positions

User clicks Load  → db.load_scenario(name)
                     engine.clear()
                     for obj in loaded: engine.add_object(obj)
                     both lists rebuilt from saved initial state
```

---

## Technologies

| Technology | Usage |
|---|---|
| Python 3 | Core language |
| Tkinter (`tk`, `ttk`) | GUI: window, canvas, widgets |
| `tkinter.colorchooser` | System colour picker dialog |
| `tkinter.messagebox` | Info / warning / confirmation dialogs |
| SQLite 3 (`sqlite3`) | Scenario persistence — no external install needed |
| `abc` (stdlib) | Abstract base classes |
| `copy.deepcopy` | Snapshot objects for initial-state tracking |
| `math` | `sqrt`, `cos`, `sin`, `atan2`, `radians`, `degrees` |
