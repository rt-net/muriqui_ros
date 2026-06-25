# Copyright 2024 RT Corporation

import os

from ament_index_python.packages import get_package_share_directory
from launch.substitutions import Command


class RobotDescriptionLoader():

    def __init__(self):
        self.robot_description_path = os.path.join(
            get_package_share_directory('muriqui_description'),
            'urdf',
            'muriqui.urdf.xacro')

        self.use_right_arm_mock = 'false'
        self.use_right_leg_mock = 'false'

        self.use_left_arm_mock = 'false'
        self.use_left_leg_mock = 'false'

        self.use_neck_mock = 'false'

        self.right_arm_port_name = '/dev/muriqui_right_arm'
        self.right_arm_config_path = 'file/path'
        self.right_leg_port_name = '/dev/muriqui_right_leg'
        self.right_leg_config_path = 'file/path'

        self.left_arm_port_name = '/dev/muriqui_left_arm'
        self.left_arm_config_path = 'file/path'
        self.left_leg_port_name = '/dev/muriqui_left_leg'
        self.left_leg_config_path = 'file/path'

        self.neck_port_name = '/dev/muriqui_neck'
        self.neck_config_path = 'file/path'

        self.baudrate = '3000000'
        self.timeout_seconds = '1.0'

        self.use_simple_collision_model = 'true'
        self.camera_default = 'true'
        self.camera_d435i = 'false'
        self.camera_d405 = 'false'

        self.use_gazebo = 'false'
        self.use_gazebo_head_camera = 'true'
        self.use_gazebo_imu = 'true'
        self.gz_control_config_package = ''
        self.gz_control_config_file_path = ''

        self.feet_fsr = 'false'
        self.arm_4joints = 'false'
        self.with_hand = 'false'

    def load(self):
        return Command([
                'xacro ',
                self.robot_description_path,
                ' use_right_arm_mock:=', self.use_right_arm_mock,
                ' use_right_leg_mock:=', self.use_right_leg_mock,

                ' use_left_arm_mock:=', self.use_left_arm_mock,
                ' use_left_leg_mock:=', self.use_left_leg_mock,

                ' use_neck_mock:=', self.use_neck_mock,

                ' right_arm_port_name:=', self.right_arm_port_name,
                ' right_arm_config_path:=', self.right_arm_config_path,
                ' right_leg_port_name:=', self.right_leg_port_name,
                ' right_leg_config_path:=', self.right_leg_config_path,

                ' left_arm_port_name:=', self.left_arm_port_name,
                ' left_arm_config_path:=', self.left_arm_config_path,
                ' left_leg_port_name:=', self.left_leg_port_name,
                ' left_leg_config_path:=', self.left_leg_config_path,

                ' neck_port_name:=', self.neck_port_name,
                ' neck_config_path:=', self.neck_config_path,

                ' baudrate:=', self.baudrate,
                ' timeout_seconds:=', self.timeout_seconds,

                ' use_simple_collision_model:=', self.use_simple_collision_model,
                ' camera_default:=', self.camera_default,
                ' camera_d435i:=', self.camera_d435i,
                ' camera_d405:=', self.camera_d405,

                ' use_gazebo:=', self.use_gazebo,
                ' use_gazebo_head_camera:=', self.use_gazebo_head_camera,
                ' use_gazebo_imu:=', self.use_gazebo_imu,
                ' gz_control_config_package:=', self.gz_control_config_package,
                ' gz_control_config_file_path:=', self.gz_control_config_file_path,

                ' feet_fsr:=', self.feet_fsr,
                ' arm_4joints:=', self.arm_4joints,
                ' with_hand:=', self.with_hand
                ])
