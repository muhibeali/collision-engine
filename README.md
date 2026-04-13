# 🧪 Collision Simulation Engine (2D)

## 📌 Overview

The **Collision Simulation Engine** is a 2D physics-based simulation project developed in Python using Object-Oriented Programming principles. The system models motion and collisions of objects (balls and blocks) inside a bounded environment.

The simulation focuses on **elastic collisions**, friction-based motion decay, and user-defined object properties. It also includes a graphical user interface (GUI) and database integration for saving and loading simulation scenarios.

---

## 🎯 Objectives

- Simulate realistic 2D object motion
- Implement elastic collision physics using momentum conservation
- Allow user interaction through a graphical interface
- Store and retrieve simulation scenarios using a database
- Provide an expandable architecture for future physics enhancements

---

## 🧠 Key Features

### 🟢 Physics Simulation
- 2D top-view motion system
- Elastic collisions between objects (momentum-based)
- Friction-based velocity decay
- Boundary constraints (objects stop when reaching screen edges)

---

### 🟡 Object Types
- Circle (Ball)
- Rectangle (Block)

Each object has:
- Mass
- Position (x, y)
- Velocity (magnitude + direction)
- Size (radius/width/height)

---

### 🔵 User Controls (GUI)
- Add objects with custom properties:
  - Mass
  - Velocity
  - Direction angle
  - Position
  - Friction coefficient
- Simulation controls:
  - Start
  - Pause
  - Reset
  - Speed control (0.5x, 1x, 1.5x, 2x)

---

### 🗄️ Database Integration
- Save simulation scenarios
- Load previous setups
- Store object configurations per scenario

---

## 🧱 System Architecture

The project follows an object-oriented modular design:
/engine → Physics engine (motion, collisions)
/objects → Ball and Block classes
/ui → Tkinter graphical interface
/database → SQLite database handler
/utils → Helper functions (math, vectors)
/main.py → Entry point of application

---

## ⚙️ Physics Model

The simulation uses simplified physics:

- Newtonian motion in 2D space
- Momentum conservation for collisions
- Perfectly elastic collisions (no energy loss)
- Friction reduces velocity over time
- Boundary condition stops objects at edges

---

## 🛠️ Technologies Used

- Python 3
- Tkinter (GUI)
- SQLite (Database)
- Object-Oriented Programming (OOP)

---

## 🚀 Future Improvements

- Angular motion (rotation and torque)
- Improved collision accuracy (continuous collision detection)
- Energy loss and restitution control
- Drag-and-drop object placement
- Graph plotting for motion analysis
- 3D simulation upgrade

---

## 👨‍💻 Project Purpose

This project is developed as part of a CS112 Object-Oriented Programming course to demonstrate:

- Application of OOP principles in real systems
- Integration of physics concepts in programming
- GUI development in Python
- Database usage for persistent storage
- Team-based software development using Git and GitHub

---

## 👥 Team Collaboration

The project is developed collaboratively using Git and GitHub with feature-based branching for parallel development.

---