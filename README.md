# ROS2 Gesture Teleop Control (Webcam)

[![ROS2 Humble](https://img.shields.io/badge/ROS2-Humble-blue)](https://docs.ros.org/en/humble/index.html)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A ROS2-based gesture control system that translates real-time human hand gestures into robot movement commands. This project demonstrates the integration of AI (MediaPipe) with Robotic Middleware (ROS2) to create an intuitive human-machine interface.

> **Project Context**: Learning ROS2 fundamentals (topics, services, actions) following the 鱼香ROS (fishros) curriculum. This project showcases incremental development — starting with keyboard control, then upgrading to gesture recognition, and finally creating an Interactive Turtle Catch Game. It demonstrates how to orchestrate multiple nodes, custom interfaces, and Docker to build a complete, containerized robotic application.

---

## 🎯 Demo
**Supported Gestures:**

<p align="center">
  <img src="assets/output.gif" alt="Gesture Control Demo" >
</p>

| **Gesture**            | **Action**      | **Functional Description**                                              |
| ---------------------- | --------------- | ----------------------------------------------------------------------- |
| ✋ **Open Palm**        | **Forward**     | Constant forward movement at default velocity.                          |
| ✊ **Closed Fist**      | **Stop / Back** | Halt movement or execute a slow reverse adjustment.                     |
| ☝️ **One Finger**      | **Turn Left**   | Rotate the turtle counter-clockwise (Yaw control).                      |
| ✌️ **Two Fingers**     | **Turn Right**  | Rotate the turtle clockwise (Yaw control).                              |
| 🤙 **Thumb & Pinky**   | **Speed Up**    | Dynamically increase the linear velocity multiplier.                    |
| 👆 **Pointing Up**     | **Speed Down**  | Decrease linear velocity for high-precision positioning.                |
| 🤘 **Rock**            | **Color Shift** | Trigger a service call to randomize the turtle's trail color.           |

---
---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────┐
│                  Client Nodes                          │
│  ┌──────────────────┐      ┌───────────────────┐       │
│  │ Keyboard Client  │      │ Gesture Client    │       │
│  │ (WASD Control)   │      │ (OpenCV+MediaPipe)│       │
│  └────────┬─────────┘      └────────┬──────────┘       │
│           │                         │                  │
│           └─────────┬───────────────┘                  │
│                     │ ROS2 Service Call                │
│                     ↓                                  │
│         ┌───────────────────────┐                      │
│         │   Service Server      │                      │
│         │ (Motion Controller)   │                      │
│         └──────────┬────────────┘                      │
│                    │ geometry_msgs/Twist               │
│                    ↓                                   │
│         ┌──────────────────────┐                       │
│         │    TurtleSim Node    │                       │
│         └──────────────────────┘                       │
└────────────────────────────────────────────────────────┘
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

This project is fully containerized to ensure "plug-and-play" deployment across different Linux environments. You can either build it locally or pull the pre-built image directly from Docker Hub.

### Option A: Pull from Docker Hub (Fastest)

You can run the game without downloading the source code by using the pre-built image:

1. **Pull the image**:
   ```bash
   docker pull xxrickxx/ros2-gesture-control:0.2.0
   ```

2. **Allow X11 Connections** (Required for GUI display):
   ```bash
   xhost +local:docker
   ```

3. **Run with Docker Compose**:
   Copy the `docker-compose.yml` from this repo to your local folder and run:
   ```bash
   docker compose up
   ```

### Option B: Build & Run Locally

If you have modified the source code, use this method:

1. **Allow X11 Connections**:
   ```bash
   xhost +local:docker
   ```

2. **Build and Launch**:
   ```bash
   docker compose up --build
   ```

### **Key Features of our Docker Setup:**

- **Instant Deployment:** Pull the image from `xxrickxx/ros2-gesture-control` and start playing in seconds.
- **GUI Forwarding:** Seamless X11 socket mapping to run `turtlesim` inside the container.
- **Hardware Access:** Direct mapping of `/dev/video*` for real-time camera inference (supports Webcams & RealSense).
- **Optimized Layers:** NumPy version locking to prevent binary compatibility issues.

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
- [x] Interactive "Turtle Catch" game logic 
- [x] Docker containerization & one-command deployment
- [ ] Gazebo TurtleBot3 integration
- [ ] Isaac Sim compatibility layer
...

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

