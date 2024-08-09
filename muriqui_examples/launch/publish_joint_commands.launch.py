# Copyright 2024 RT Corporation

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    declare_file = DeclareLaunchArgument(
        'file',
        default_value='joint_goals',
        description='Set csv file name for joint goals.'
    )

    config_dir = get_package_share_directory(
        'muriqui_examples') + '/config/'

    publish_joint_commands = Node(
        package='muriqui_examples',
        executable='publish_joint_commands.py',
        output='screen',
        arguments=['--csv_filepath', [config_dir, LaunchConfiguration('file'), '.csv']],
    )

    ld = LaunchDescription()
    ld.add_action(declare_file)
    ld.add_action(publish_joint_commands)

    return ld
