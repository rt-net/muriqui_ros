
# Muriqui Description

## Requirements

- ROS 2 Humble Hawksbill

## Installation

```bash
# Setup ROS environment
source /opt/ros/humble/setup.bash

# Place this package in your ROS 2 workspace (e.g. ~/ros2_ws/src)

# Install dependencies
cd ~/ros2_ws/src
rosdep install -r -y -i --from-paths .

# Build & Install
cd ~/ros2_ws
colcon build --symlink-install
```

## Usage

Display robot model in RViz 2.

```bash
source ~/ros2_ws/install/setup.bash

# With joint state publisher GUI
ros2 launch muriqui_description display.launch.py jsp_gui:=true

# With joint state publisher
ros2 launch muriqui_description display.launch.py jsp:=true

# Without joint state publishers
ros2 launch muriqui_description display.launch.py

# With 4-axis arm option
ros2 launch muriqui_description display.launch.py arm_4joints:=true

# With 4-axis arm and hand option
ros2 launch muriqui_description display.launch.py with_hand:=true

# With head camera D435i option
ros2 launch muriqui_description display.launch.py camera_d435i:=true

# With head camera D405 option
ros2 launch muriqui_description display.launch.py camera_d405:=true

# With feet FSR sensors option
ros2 launch muriqui_description display.launch.py feet_fsr:=true
```

### Generate URDF file

```bash
cd /path/to/muriqui_description
cd urdf
xacro muriqui.urdf.xacro -o muriqui.urdf

# When using the 4-axis arm, update the urdf file with the following command
xacro muriqui.urdf.xacro -o muriqui.urdf arm_4joints:=true

# When using the 4-axis arm and hand, update the urdf file with the following command
xacro muriqui.urdf.xacro -o muriqui.urdf with_hand:=true
```
