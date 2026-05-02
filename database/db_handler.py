import sqlite3
from objects.ball import Ball
from objects.block import Block
from utils.vector import Vector


class DBHandler:
    def __init__(self, path: str = "simulation.db"):
        self.path = path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.path) as conn:
            # Friction is a single global value stored per scenario, not per object
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scenarios (
                    id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    name     TEXT UNIQUE NOT NULL,
                    friction REAL NOT NULL DEFAULT 0.02
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS objects (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario_id INTEGER NOT NULL,
                    type        TEXT NOT NULL,
                    pos_x       REAL, pos_y   REAL,
                    vel_x       REAL, vel_y   REAL,
                    mass        REAL, color   TEXT,
                    radius      REAL,
                    width       REAL, height  REAL,
                    FOREIGN KEY (scenario_id) REFERENCES scenarios(id) ON DELETE CASCADE
                )
            """)
            conn.commit()

        # Migration: add friction column to existing DBs that were created without it
        try:
            with sqlite3.connect(self.path) as conn:
                conn.execute(
                    "ALTER TABLE scenarios ADD COLUMN friction REAL NOT NULL DEFAULT 0.02"
                )
                conn.commit()
        except sqlite3.OperationalError:
            pass  # column already exists

    def save_scenario(self, name: str, objects: list, friction: float = 0.02):
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO scenarios (name, friction) VALUES (?, ?)",
                (name, friction)
            )
            scenario_id = conn.execute(
                "SELECT id FROM scenarios WHERE name = ?", (name,)
            ).fetchone()[0]
            conn.execute("DELETE FROM objects WHERE scenario_id = ?", (scenario_id,))

            for obj in objects:
                if isinstance(obj, Ball):
                    conn.execute(
                        "INSERT INTO objects "
                        "(scenario_id, type, pos_x, pos_y, vel_x, vel_y, mass, color, radius) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (scenario_id, "ball",
                         obj.position.x, obj.position.y,
                         obj.velocity.x, obj.velocity.y,
                         obj.mass, obj.color, obj.radius)
                    )
                elif isinstance(obj, Block):
                    conn.execute(
                        "INSERT INTO objects "
                        "(scenario_id, type, pos_x, pos_y, vel_x, vel_y, mass, color, width, height) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (scenario_id, "block",
                         obj.position.x, obj.position.y,
                         obj.velocity.x, obj.velocity.y,
                         obj.mass, obj.color, obj.width, obj.height)
                    )
            conn.commit()

    def load_scenario(self, name: str) -> tuple:
        """Returns (list[BaseObject], friction: float)."""
        with sqlite3.connect(self.path) as conn:
            row = conn.execute(
                "SELECT id, friction FROM scenarios WHERE name = ?", (name,)
            ).fetchone()
            if not row:
                return [], 0.02
            scenario_id, friction = row
            rows = conn.execute(
                "SELECT type, pos_x, pos_y, vel_x, vel_y, mass, color, radius, width, height "
                "FROM objects WHERE scenario_id = ?", (scenario_id,)
            ).fetchall()

        objects = []
        for r in rows:
            obj_type, px, py, vx, vy, mass, color, radius, width, height = r
            pos = Vector(px, py)
            vel = Vector(vx, vy)
            color = color or "#3498db"
            if obj_type == "ball":
                objects.append(Ball(pos, vel, mass, radius, color))
            elif obj_type == "block":
                objects.append(Block(pos, vel, mass, width, height, color))
        return objects, friction

    def list_scenarios(self) -> list:
        with sqlite3.connect(self.path) as conn:
            rows = conn.execute(
                "SELECT name FROM scenarios ORDER BY name"
            ).fetchall()
        return [r[0] for r in rows]

    def delete_scenario(self, name: str):
        """Delete a scenario and all its objects (cascade handled by FK)."""
        with sqlite3.connect(self.path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("DELETE FROM scenarios WHERE name = ?", (name,))
            conn.commit()
