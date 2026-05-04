# ROS2 Gesture Teleop Control (RealSense/Webcam)

[![ROS2 Humble](https://img.shields.io/badge/ROS2-Humble-blue)](https://docs.ros.org/en/humble/index.html)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A ROS2-based gesture control system that translates real-time human hand gestures into robot movement commands. This project demonstrates the integration of AI (MediaPipe) with Robotic Middleware (ROS2) to create an intuitive human-machine interface.

> **Project Context**: Learning ROS2 fundamentals (topics, services, actions) following the 鱼香ROS (fishros) curriculum. This project showcases incremental development — starting with keyboard control, then upgrading to gesture recognition, and finally containerizing for easy deployment.
---
## 🎯 Demo
**Supported Gestures:**

- ✋ Open palm   → Forward
- ✊ Closed fist → Backward
- ☝️ One-finger  → Turn left
- ✌️ Two-finger  → Turn right
  
---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Client Nodes                            │
│  ┌──────────────────┐      ┌───────────────────┐       │
│  │ Keyboard Client  │      │ Gesture Client    │       │
│  │ (WASD Control)   │      │ (OpenCV+MediaPipe)│       │
│  └────────┬─────────┘      └────────┬──────────┘       │
│           │                         │                   │
│           └─────────┬───────────────┘                   │
│                     │ ROS2 Service Call                 │
│                     ↓                                    │
│         ┌───────────────────────┐                       │
│         │   Service Server      │                       │
│         │ (Motion Controller)   │                       │
│         └──────────┬────────────┘                       │
│                    │ geometry_msgs/Twist                │
│                    ↓                                     │
│         ┌──────────────────────┐                        │
│         │    TurtleSim Node    │                        │
│         └──────────────────────┘                        │
└─────────────────────────────────────────────────────────┘
```
---

## 🚀 Quick Start (Local Installation)

### 1. Prerequisites
*   **OS:** Ubuntu 22.04 LTS
*   **ROS2:** Humble (Desktop Install)
*   **Python:** 3.10
*   **Hardware:** Webcam or Intel RealSense Camera

### 2. Dependencies
```bash
pip install mediapipe==0.10.14 opencv-python readchar "numpy<2"
```

### 3. Build the Project

```
# Clone the repository
git clone https://github.com/XxRickxX/ros2-gesture-control.git .
cd ros2-gesture-control

# Build
colcon build --packages-select ges_cl_interface gesture_control_python

# Source the environment
source install/setup.bash
```

### 4. Execution
Open three terminals and source each:
```bash
# Terminal 1: Simulator
ros2 run turtlesim turtlesim_node

# Terminal 2: Control Server
ros2 run gesture_control_python service_turtle_control

# Terminal 3: Gesture Client (Camera)
ros2 run gesture_control_python client_turtle_control_gesture
```
*Tip: You can also use the launch file:* `ros2 launch gesture_control_python gesture_control.launch.py`

---

## 🐳 Docker Deployment (Containerized)

This project is fully containerized to ensure "plug-and-play" deployment across different Linux environments.



1.  **Allow X11 Connections** (for GUI display):
    ```bash
    xhost +local:docker
    ```
2.  **Run with Docker Compose**:
    ```bash
    docker compose up --build
    ```

**Key Features of our Docker Setup:**
*   **GUI Forwarding:** Seamless X11 socket mapping to run `turtlesim` inside the container.
*   **Hardware Access:** Direct mapping of `/dev/video*` for real-time camera inference.
*   **Optimized Layers:** NumPy version locking to prevent binary compatibility issues.

---

## 💼 About This Project

**Purpose**: Translate ROS2 theoretical knowledge into a working system through practical implementation.

**Problem Solved**: Most robotics tutorials require physical hardware. This project demonstrates core ROS2 concepts (service communication, launch files, modular architecture) using only a webcam and simulation — removing the hardware barrier for learners and showcasing software engineering practices.

**Engineering Highlights**:
- ✅ **Modular Design**: Separated gesture detection, control logic, and robot interface into independent nodes
- ✅ **Iterative Development**: Built incrementally (keyboard → gesture → Docker) with git history showing progression
- ✅ **Reproducibility**: Docker Compose setup eliminates "works on my machine" issues
- ✅ **Production Mindset**: Includes error handling, parameter configuration, and performance metrics

**Current Status**: Actively learning ROS2 (following 鱼香ROS curriculum). This project will evolve as I progress through navigation, perception, and manipulation modules.

---

## 🗺️ Roadmap

- [x] Basic turtle control with ROS2 service architecture
- [x] Keyboard control client (WASD input)
- [x] Gesture recognition with MediaPipe
- [x] Docker containerization & one-command deployment
- [ ] Gazebo TurtleBot3 integration
- [ ] Isaac Sim compatibility layer
- [ ] Multi-robot gesture orchestration

---

## 📄 License

This project is licensed under the **Apache License 2.0**. 

Feel free to use this project for learning, research, or as a base for your own ROS2 applications. If you find it helpful, a star ⭐ would be much appreciated!

---

## 🙏 Acknowledgments

- **鱼香ROS (Fishros)** - Comprehensive ROS2 tutorial series
- **古月居 (Guyuehome)** - ROS ecosystem knowledge base
- **Joyous 工程師の師** - [MediaPipe hand tracking implementation guide](https://www.youtube.com/@Joyous-Code_Teacher)
- **MediaPipe Team (Google)** - Open-source hand landmark detection framework

---

## 🔖 Tags

`#ROS2` `#Robotics` `#ComputerVision` `#Docker` `#EmbodiedAI` `#LearningInPublic` `#LearningByDoing`

