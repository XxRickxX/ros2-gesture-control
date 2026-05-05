FROM osrf/ros:humble-desktop

# Avoid interactive prompts during apt install
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /root/ros2_ws

# Install system dependencies (including GUI and Camera libs)
RUN apt-get update && apt-get install -y \
    python3-pip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    usbutils \
    v4l-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (Fixed versions to avoid NumPy 2.x conflicts)
RUN pip3 install --no-cache-dir \
    "numpy<2" \
    mediapipe==0.10.14 \
    opencv-python \
    readchar

# Copy source code
COPY src/ /root/ros2_ws/src/

# Build ROS2 workspace
RUN . /opt/ros/humble/setup.sh && \
    colcon build --symlink-install

# Add setup to bashrc for interactive sessions
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc && \
    echo "source /root/ros2_ws/install/setup.bash" >> ~/.bashrc

# Entrypoint script to source environment automatically
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
# Default command: launch the whole system
# CMD ["ros2", "launch", "gesture_control_python", "gesture_control.launch.py"]
CMD ["ros2", "launch", "gesture_control_python", "gesture_game.launch.py"]