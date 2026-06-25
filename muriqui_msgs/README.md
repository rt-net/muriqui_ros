# Muriqui Messages

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

## License

This softwware is licensed under the RT Cor. Software License Version 1.0.
See the [LICENSE](LICENSE) file for details.
