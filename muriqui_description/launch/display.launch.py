# Copyright 2024 RT Corporation

from ament_index_python.packages import get_package_share_directory
from muriqui_description.robot_description_loader import RobotDescriptionLoader
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    declare_jsp_gui = DeclareLaunchArgument(
        'jsp_gui', default_value='false',
        description=('Set "true" to launch joint state publisher gui.')
    )

    declare_jsp = DeclareLaunchArgument(
        'jsp', default_value='false',
        description=('Set "true" to launch joint state publisher.')
    )

    declare_simple_collision = DeclareLaunchArgument(
        'simple_collision', default_value='true',
        description=('Set "true" to use simple collision model.')
    )

    declare_feet_fsr = DeclareLaunchArgument(
        'feet_fsr', default_value='false',
        description=('Set "true" to use feet FSR sensors.')
    )

    declare_arm_4joints = DeclareLaunchArgument(
        'arm_4joints', default_value='false',
        description=('Set "true" to use arm joint 4DoF model')
    )

    declare_with_hand = DeclareLaunchArgument(
        'with_hand', default_value='false',
        description=('Set "true" to use with hand model')
    )

    declare_camera_default = DeclareLaunchArgument(
        'camera_default', default_value='true',
        description=('Set "true" to use camera default model')
    )

    declare_camera_d435i = DeclareLaunchArgument(
        'camera_d435i', default_value='false',
        description=('Set "true" to use camera D435i model')
    )

    declare_camera_d405 = DeclareLaunchArgument(
        'camera_d405', default_value='false',
        description=('Set "true" to use camera D405 model')
    )

    description_loader = RobotDescriptionLoader()
    description_loader.use_simple_collision_model = LaunchConfiguration('simple_collision')
    description_loader.arm_4joints = LaunchConfiguration('arm_4joints')
    description_loader.with_hand = LaunchConfiguration('with_hand')
    description_loader.camera_default = LaunchConfiguration('camera_default')
    description_loader.camera_d435i = LaunchConfiguration('camera_d435i')
    description_loader.camera_d405 = LaunchConfiguration('camera_d405')

    description_loader.feet_fsr = LaunchConfiguration('feet_fsr')

    declare_robot_description = DeclareLaunchArgument(
        'loaded_description',
        default_value=description_loader.load(),
        description='Set robot_description text.'
    )

    rsp = Node(package='robot_state_publisher',
               executable='robot_state_publisher',
               output='both',
               parameters=[{'robot_description': LaunchConfiguration('loaded_description')}])
    jsp_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        output='screen',
        condition=IfCondition(LaunchConfiguration('jsp_gui')),
        )

    jsp = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        output='screen',
        condition=IfCondition(LaunchConfiguration('jsp')),
        parameters=[{
            'source_list': ["updated_joint_states"],
            'rate': 100,
        }]
        )

    rviz_config_file = get_package_share_directory(
        'muriqui_description') + '/launch/config.rviz'

    declare_rviz_config = DeclareLaunchArgument(
        'rviz_config',
        default_value=rviz_config_file,
        description='Set file path to RViz config file.'
    )

    rviz = Node(package='rviz2',
                executable='rviz2',
                name='rviz2',
                output='log',
                arguments=['-d', LaunchConfiguration('rviz_config')]
                )

    ld = LaunchDescription()
    ld.add_action(declare_jsp_gui)
    ld.add_action(declare_jsp)
    ld.add_action(declare_simple_collision)
    ld.add_action(declare_arm_4joints)
    ld.add_action(declare_with_hand)
    ld.add_action(declare_camera_default)
    ld.add_action(declare_camera_d435i)
    ld.add_action(declare_camera_d405)
    ld.add_action(declare_feet_fsr)
    ld.add_action(declare_robot_description)
    ld.add_action(declare_rviz_config)
    ld.add_action(rsp)
    ld.add_action(jsp_gui)
    ld.add_action(jsp)
    ld.add_action(rviz)

    return ld
