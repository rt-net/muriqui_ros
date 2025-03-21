import os

from ament_index_python.packages import get_package_share_directory
from muriqui_description.robot_description_loader import RobotDescriptionLoader
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import ExecuteProcess
from launch.actions import OpaqueFunction
from launch.conditions import IfCondition
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

    declare_with_hand = DeclareLaunchArgument(
        'with_hand', default_value='false',
        description=('Set "true" to use with hand model')
    )

    rdl = RobotDescriptionLoader()
    rdl.arm_4joints = LaunchConfiguration('arm_4joints')
    rdl.with_hand = LaunchConfiguration('hand_model')

    declare_loaded_description = DeclareLaunchArgument(
        'loaded_description',
        default_value=rdl.load(),
        description='Set robot_description text.  \
                     It is recommended to use RobotDescriptionLoader() in muriqui_description.'
    )

    declare_feet_fsr = DeclareLaunchArgument(
        'feet_fsr', default_value='false',
        description=('Set "true" to use feet FSR sensors.')
    )

    def gen_controller_manager(context):
        params = []
        params.append({'robot_description': LaunchConfiguration('loaded_description')})

        if context.launch_configurations['arm_4joints'] == 'true':
            params.append(config_path('muriqui_controllers_arm4.yaml'))
        elif context.launch_configurations['with_hand'] == 'true':
            params.append(config_path('muriqui_controllers_arm4_with_hand.yaml'))
        else:
            params.append(config_path('muriqui_controllers.yaml'))

        if context.launch_configurations['feet_fsr'] == 'true':
            params.append(config_path('feet_fsr_broadcaster.yaml'))

        return [Node(
            package='controller_manager',
            executable='ros2_control_node',
            parameters=params,
            output='screen',
            )]

    controller_manager = OpaqueFunction(function=gen_controller_manager)

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

    spawn_feet_fsr_broadcaster = ExecuteProcess(
                cmd=['ros2 run controller_manager spawner feet_fsr_broadcaster'],
                shell=True,
                output='screen',
                condition=IfCondition(LaunchConfiguration('feet_fsr'))
            )

    return LaunchDescription([
        declare_arm_4joints,
        declare_with_hand,
        declare_loaded_description,
        declare_feet_fsr,
        controller_manager,
        spawn_joint_state_broadcaster,
        spawn_right_arm_controller,
        spawn_right_leg_controller,
        spawn_left_arm_controller,
        spawn_left_leg_controller,
        spawn_neck_controller,
        spawn_feet_fsr_broadcaster
    ])
