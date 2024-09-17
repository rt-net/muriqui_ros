import os

from ament_index_python.packages import get_package_share_directory
from muriqui_description.robot_description_loader import RobotDescriptionLoader
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import ExecuteProcess
from launch.actions import OpaqueFunction
from launch.actions import SetLaunchConfiguration
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def config_path(file_name: str) -> str:
    return os.path.join(
        get_package_share_directory('muriqui_control'),
        'config',
        file_name
    )


def generate_launch_description():
    declare_arm_4joints = DeclareLaunchArgument(
        'arm_4joints', default_value='false',
        description=('Set "true" to use arm joint 4DoF model')
    )

    rdl = RobotDescriptionLoader()
    rdl.arm_4joints = LaunchConfiguration('arm_4joints')

    declare_loaded_description = DeclareLaunchArgument(
        'loaded_description',
        default_value=rdl.load(),
        description='Set robot_description text.  \
                     It is recommended to use RobotDescriptionLoader() in muriqui_description.'
    )

    CONTROLLER_PARAM_CONFIG = "controller_param_config"

    def controller_param_configuration(context):
        param_path = config_path('muriqui_controllers.yaml')
        if context.launch_configurations['arm_4joints'] == 'true':
            param_path = config_path('muriqui_controllers_arm4.yaml')

        return [SetLaunchConfiguration(name=CONTROLLER_PARAM_CONFIG, value=param_path)]
    set_controller_param_config = OpaqueFunction(function=controller_param_configuration)

    controller_manager = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[{'robot_description': LaunchConfiguration('loaded_description')},
                    LaunchConfiguration(CONTROLLER_PARAM_CONFIG)],
        output='screen',
        )

    spawn_joint_state_broadcaster = ExecuteProcess(
                cmd=['ros2 run controller_manager spawner joint_state_broadcaster'],
                shell=True,
                output='screen',
            )

    spawn_right_arm_controller = ExecuteProcess(
                cmd=['ros2 run controller_manager spawner right_arm_controller'],
                shell=True,
                output='screen',
            )

    spawn_left_arm_controller = ExecuteProcess(
                cmd=['ros2 run controller_manager spawner left_arm_controller'],
                shell=True,
                output='screen',
            )

    spawn_right_leg_controller = ExecuteProcess(
                cmd=['ros2 run controller_manager spawner right_leg_controller'],
                shell=True,
                output='screen',
            )

    spawn_left_leg_controller = ExecuteProcess(
                cmd=['ros2 run controller_manager spawner left_leg_controller'],
                shell=True,
                output='screen',
            )

    spawn_neck_controller = ExecuteProcess(
                cmd=['ros2 run controller_manager spawner neck_controller'],
                shell=True,
                output='screen',
            )

    return LaunchDescription([
        declare_arm_4joints,
        declare_loaded_description,
        set_controller_param_config,

        controller_manager,
        spawn_joint_state_broadcaster,
        spawn_right_arm_controller,
        spawn_right_leg_controller,
        spawn_left_arm_controller,
        spawn_left_leg_controller,
        spawn_neck_controller,
    ])
