# Copyright 2024 RT Corporation

import os

from ament_index_python.packages import get_package_share_directory
from muriqui_description.robot_description_loader import RobotDescriptionLoader
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import EmitEvent
from launch.actions import IncludeLaunchDescription
from launch.actions import OpaqueFunction
from launch.actions import RegisterEventHandler
from launch.actions import SetLaunchConfiguration
from launch.events import matches_action
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PythonExpression
from launch_ros.actions import LifecycleNode
from launch_ros.actions import Node
from launch_ros.events import lifecycle
from launch_ros.event_handlers import OnStateTransition
from lifecycle_msgs.msg import Transition


def config_path(file_name: str) -> str:
    return os.path.join(
        get_package_share_directory('muriqui_hardware'),
        'config',
        file_name
    )


def generate_launch_description():
    declare_mock = DeclareLaunchArgument(
        'mock',
        default_value='false',
        description='Set "true" to use mock hardware.'
    )

    declare_use_camera = DeclareLaunchArgument(
        'use_camera',
        default_value='true',
        description='Set "true" to use head camera.'
    )

    declare_video_device = DeclareLaunchArgument(
        'video_device',
        default_value='/dev/muriqui_head_camera',
        description='Set a device file path for head camera.'
    )

    declare_use_imu = DeclareLaunchArgument(
        'use_imu',
        default_value='true',
        description='Set "true" to use IMU module.'
    )

    declare_imu_device = DeclareLaunchArgument(
        'imu_device',
        default_value='/dev/muriqui_imu',
        description='Set a device file path for IMU.'
    )

    declare_use_board = DeclareLaunchArgument(
        'use_board',
        default_value='true',
        description='Set "true" to use Muriqui board.'
    )

    declare_board_device = DeclareLaunchArgument(
        'board_device',
        default_value='/dev/muriqui_board',
        description='Set a device file path for Muriqui board.'
    )

    declare_feet_fsr = DeclareLaunchArgument(
        'feet_fsr', default_value='false',
        description=('Set "true" to use feet FSR sensors.')
    )

    declare_arm_4joints = DeclareLaunchArgument(
        'arm_4joints', default_value='false',
        description=('Set "true" to use arm joint 4DoF model')
    )

    declare_camera_d435i = DeclareLaunchArgument(
        'camera_d435i', default_value='false',
        description=('Set "true" to use camera d435i')
    )
    R_ARM_CONFIG = "r_arm_config"
    L_ARM_CONFIG = "l_arm_config"

    def arm_configuration(context, config_name: str, prefix: str):
        param_path = config_path(prefix + '_arm.yaml')
        if context.launch_configurations['arm_4joints'] == 'true':
            param_path = config_path(prefix + '_arm4.yaml')

        return [SetLaunchConfiguration(name=config_name, value=param_path)]

    set_right_arm_config = OpaqueFunction(function=arm_configuration, args=[R_ARM_CONFIG, 'right'])
    set_left_arm_config = OpaqueFunction(function=arm_configuration, args=[L_ARM_CONFIG, 'left'])

    rdl = RobotDescriptionLoader()
    rdl.use_right_arm_mock = LaunchConfiguration('mock')
    rdl.use_right_leg_mock = LaunchConfiguration('mock')
    rdl.use_left_arm_mock = LaunchConfiguration('mock')
    rdl.use_left_leg_mock = LaunchConfiguration('mock')
    rdl.use_neck_mock = LaunchConfiguration('mock')
    rdl.arm_4joints = LaunchConfiguration('arm_4joints')
    rdl.camera_d435i = LaunchConfiguration('camera_d435i')

    rdl.right_arm_port_name = '/dev/muriqui_right_arm'
    rdl.right_leg_port_name = '/dev/muriqui_right_leg'
    rdl.left_arm_port_name = '/dev/muriqui_left_arm'
    rdl.left_leg_port_name = '/dev/muriqui_left_leg'
    rdl.neck_port_name = '/dev/muriqui_neck'
    rdl.right_arm_config_path = LaunchConfiguration(R_ARM_CONFIG)
    rdl.left_arm_config_path = LaunchConfiguration(L_ARM_CONFIG)

    rdl.right_leg_config_path = config_path('right_leg.yaml')

    rdl.left_leg_config_path = config_path('left_leg.yaml')

    rdl.neck_config_path = config_path('neck.yaml')

    rdl.feet_fsr = LaunchConfiguration('feet_fsr')

    rdl.baudrate = '4000000'
    rdl.timeout_seconds = '1.0'

    description = rdl.load()

    control_node = IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                get_package_share_directory('muriqui_control'),
                '/launch/muriqui_control.launch.py']),
            launch_arguments={
                'loaded_description': description,
                'feet_fsr': LaunchConfiguration('feet_fsr'),
                'arm_4joints': rdl.arm_4joints,
                }.items()
        )

    display_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                get_package_share_directory('muriqui_description'),
                '/launch/display.launch.py']),
            launch_arguments={
                'loaded_description': description,
                'jsp_gui': 'false',
                'jsp': 'false',
                'feet_fsr': LaunchConfiguration('feet_fsr'),
                'arm_4joints': rdl.arm_4joints,
                'camera_d435i': rdl.camera_d435i,
                }.items()
        )

    camera_info_file = 'file://' + get_package_share_directory(
        'muriqui_examples') + '/config/camera_info.yaml'

    usb_cam_node = Node(
        package='usb_cam',
        executable='usb_cam_node_exe',
        namespace='head_camera/color',
        parameters=[
            {'camera_name': 'head_camera'},
            {'video_device': LaunchConfiguration('video_device')},
            {'camera_info_url': camera_info_file},
            {'frame_rate': 30.0},
            {'frame_id': 'head_camera_color_optical_frame'},
            {'image_height': 720},
            {'image_width': 1280},
            {'pixel_format': 'mjpeg2rgb'}
        ],
        condition=IfCondition(
            PythonExpression(
                ["'", LaunchConfiguration('use_camera'),
                 "' == 'true' and '", LaunchConfiguration('camera_d435i'),
                 "' == 'false'"]
            )
        )
    )

    d435i_cam_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            get_package_share_directory('realsense2_camera'),
            '/launch/rs_launch.py']),
        launch_arguments={
            'camera_namespace': '',
            'camera_name': 'head_camera',
            'device_type': 'd435i',
            'rgb_camera.profile': '1280x720x30',
            'depth_module.profile': '1280x720x30',
            'pointcloud.enable': 'true',
            'align_depth.enable': 'true',
            'publish_tf': 'true',
        }.items(),
        condition=IfCondition(
            PythonExpression(
                ["'", LaunchConfiguration('use_camera'),
                 "' == 'true' and '", LaunchConfiguration('camera_d435i'),
                 "' == 'true'"]
            )
        )
    )

    imu = LifecycleNode(
        namespace='',
        name='rt_usb_9axisimu_driver',
        package='rt_usb_9axisimu_driver',
        executable='rt_usb_9axisimu_driver',
        output='screen',
        parameters=[{
            'port': LaunchConfiguration('imu_device'),
        }],
        condition=IfCondition(LaunchConfiguration('use_imu'))
    )

    emit_configuring_event = EmitEvent(
        event=lifecycle.ChangeState(
            lifecycle_node_matcher=matches_action(imu),
            transition_id=Transition.TRANSITION_CONFIGURE,
        )
    )

    emit_activating_event = EmitEvent(
        event=lifecycle.ChangeState(
            lifecycle_node_matcher=matches_action(imu),
            transition_id=Transition.TRANSITION_ACTIVATE,
        )
    )

    register_activating_transition = RegisterEventHandler(
        OnStateTransition(
            target_lifecycle_node=imu,
            goal_state='inactive',
            entities=[
                emit_activating_event
            ],
        )
    )

    muriqui_board = Node(
        package='muriqui_hardware',
        executable='muriqui_board_node.py',
        name='muriqui_board',
        output='screen',
        parameters=[
            {'port': LaunchConfiguration('board_device')},
            {'baudrate': 115200},
        ],
        condition=IfCondition(LaunchConfiguration('use_imu'))
    )

    return LaunchDescription([
        declare_mock,
        declare_use_camera,
        declare_video_device,
        declare_use_imu,
        declare_imu_device,
        declare_use_board,
        declare_board_device,
        declare_feet_fsr,
        declare_arm_4joints,
        declare_camera_d435i,
        set_right_arm_config,
        set_left_arm_config,
        control_node,
        display_launch,
        usb_cam_node,
        d435i_cam_node,
        imu,
        register_activating_transition,
        emit_configuring_event,
        muriqui_board
    ])
