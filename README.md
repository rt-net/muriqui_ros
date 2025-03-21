# muriqui_ros

## Requirements

- ROS 2 Humble Hawksbill

## Installation

### Download package

```bash
mkdir -p ~/muriqui_ws/src
cd ~/muriqui_ws/src
# Download muriqui_ros, muriqui_description, muriqui_msgs and rt_manipulators_cpp here
```

### Install dependencies

```bash
cd ~/muriqui_ws/src
rosdep install -iry --from-paths .
```

### Build

```bash
cd ~/muriqui_ws
colcon build --symlink-install
```

### Create udev rules

Execute the following command to create symbolic links to devices such as camera, IMU, etc.

```bash
# This command creates symbolic links (e.g. /dev/muriqui_head_camera, /dev/muriqui_imu).
source ~/muriqui_ws/install/setup.bash 
ros2 run muriqui_tools create_udev_rules.sh
```

## Usage

### Install ROS environment

Execute the following command in each new terminal before using ROS 2 commands:

```bash
source ~/muriqui_ws/install/setup.bash 
```

### Create symbolic links

This command creates symbolic links of USB devices.
You must execute this command before using the real robot.

```bash
ros2 run muriqui_hardware create_symbolic_links 
```

### Launch real robot

Execute the following command to launch the Muriqui

```bash
ros2 launch muriqui_examples demo.launch.py mock:=false
```

Execute the following command to launch the muriqui without the sensors:

```bash
ros2 launch muriqui_examples demo.launch.py mock:=false use_head_camera:=false use_imu:=false
```

### Launch real robot with mock hardware

You can replace the servo motors with mocks to test your application.
Execute the following command to launch the Muriqui with mock hardware:

```bash
ros2 launch muriqui_examples demo.launch.py mock:=true
```

### Launch Gazebo simulator

Instead of running the real robot, you can simulate it on Gazebo.
Execute the following command to launch the muriqui in gazebo:

```bash
ros2 launch muriqui_gazebo muriqui_gazebo.launch.py
```

Execute the following command to launch the muriqui in gazebo without the sensors:

```bash
ros2 launch muriqui_gazebo muriqui_gazebo.launch.py use_head_camera:=false use_imu:=false
```

### Launch Customized hardware

Execute the following command to launch the custom 4-axis arm model of the Muriqui:

```bash
# This case is launch real robot
ros2 launch muriqui_examples demo.launch.py mock:=false arm_4joints:=true
```

Execute the following command to launch the custom 4-axis arm and hand model of the Muriqui:

```bash
# This case is launch real robot
ros2 launch muriqui_examples demo.launch.py mock:=false with_hand:=true
```

The custom head camera realsense D435i of the Muriqui:

```bash
ros2 launch muriqui_examples demo.launch.py camera_d435i:=true
```

The custom head camera realsense D405 of the Muriqui:

```bash
ros2 launch muriqui_examples demo.launch.py camera_d405:=true
```

Feet FSR sensors:

```bash
ros2 launch muriqui_examples demo.launch.py feet_fsr:=true
```

## Examples

Please refer to the [muriqui_examples](muriqui_examples/README.md) for examples.

## License

This softwware is licensed under the RT Cor. Software License Version 1.0.
See the [LICENSE](LICENSE) file for details.
