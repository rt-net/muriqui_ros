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

### Install custom ros2_control package

```bash
sudo apt install python3-vcstool
cd ~/ros2_control_ws/src
vcs import < ~/muriqui_ws/src/muriqui_ros/muriqui_ros.repos

rosdep install -iry --from-paths . 

cd ~/ros2_control_ws
colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release
```

### Install other dependencies

```bash
source ~/ros2_control_ws/install/setup.bash

cd ~/muriqui_ws/src
rosdep install -iry --from-paths .
```

### Build

```bash
source ~/ros2_control_ws/install/setup.bash

cd ~/muriqui_ws
colcon build --symlink-install
```

## Usage

### Install ROS environment

Execute the following command in each new terminal before using ROS 2 commands:

```bash
source ~/ros2_control_ws/install/setup.bash
source ~/muriqui_ws/install/setup.bash 
```

### Launch Gazebo simulator

Execute the following command to launch the muriqui in gazebo:

```bash
ros2 launch muriqui_gazebo muriqui_gazebo.launch.py
```

Execute the following command to launch the muriqui in gazebo without the sensors:

```bash
ros2 launch muriqui_gazebo muriqui_gazebo.launch.py use_head_camera:=false use_imu:=false
```

### Create symbolic links

This command creates symbolic links of USB devices.
You must execute this command before using the real robot.

```bash
ros2 run muriqui_hardware create_symbolic_links 
```

### Launch real robot with mock hardware

Execute the following command to launch the Muriqui with mock hardware:

```bash
ros2 launch muriqui_examples demo.launch.py mock:=true
```

### Launch real robot

Execute the following command to launch the Muriqui

```bash
ros2 launch muriqui_examples demo.launch.py mock:=false
```

## Examples

Please refer to the [muriqui_examples](muriqui_examples/README.md) for examples.

## License

This softwware is licensed under the RT Cor. Software License Version 1.0.
See the [LICENSE](LICENSE) file for details.
