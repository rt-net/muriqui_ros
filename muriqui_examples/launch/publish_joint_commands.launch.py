# Copyright 2024 RT Corporation

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    csv_filepath = get_package_share_directory(
        'muriqui_examples') + '/config/joint_goals.csv'

    publish_joint_commands = Node(
        package='muriqui_examples',
        executable='publish_joint_commands.py',
        output='screen',
        arguments=['--csv_filepath', csv_filepath],
    )

    ld = LaunchDescription()
    ld.add_action(publish_joint_commands)

    return ld
