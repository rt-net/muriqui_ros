import os

from ament_index_python.packages import get_package_share_directory
from muriqui_description.robot_description_loader import RobotDescriptionLoader
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import ExecuteProcess
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.actions import SetParameter


def generate_launch_description():
    declare_use_head_camera = DeclareLaunchArgument(
        'use_head_camera',
        default_value='true',
        description='Set false to disable head camera.'
    )

    declare_use_imu = DeclareLaunchArgument(
        'use_imu',
        default_value='true',
        description='Set false to disable IMU.'
    )

    declare_arm_4joints = DeclareLaunchArgument(
        'arm_4joints',
        default_value='false',
        description=('Set "true" to use arm joint 4DoF model')
    )

    declare_with_hand = DeclareLaunchArgument(
        'with_hand',
        default_value='false',
        description=('Set "true" to use with hand model')
    )

    description_loader = RobotDescriptionLoader()
    description_loader.use_gazebo = 'true'
    description_loader.use_gazebo_head_camera = LaunchConfiguration('use_head_camera')
    description_loader.use_gazebo_imu = LaunchConfiguration('use_imu')
    description_loader.arm_4joints = LaunchConfiguration('arm_4joints')
    description_loader.with_hand = LaunchConfiguration('with_hand')
    description_loader.gz_control_config_package = 'muriqui_control'

    description_loader.gz_control_config_file_path = PythonExpression(
        ["'config/muriqui_controllers_arm4.yaml' if '",
         LaunchConfiguration('arm_4joints'),
         "' == 'true' else 'config/muriqui_controllers_arm4_with_hand.yaml' if '",
         LaunchConfiguration('with_hand'),
         "' == 'true' else 'config/muriqui_controllers.yaml'"])

    description = description_loader.load()

    display_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                get_package_share_directory('muriqui_description'),
                '/launch/display.launch.py']),
            launch_arguments={
                'loaded_description': description,
                'jsp_gui': 'false',
                'jsp': 'false',
                'arm_4joint4': description_loader.arm_4joints,
                'with_hand': description_loader.with_hand,
                }.items()
        )

    # PATHを追加で通さないとSTLファイルが読み込まれない
    env = {'IGN_GAZEBO_SYSTEM_PLUGIN_PATH': os.environ['LD_LIBRARY_PATH'],
           'IGN_GAZEBO_RESOURCE_PATH': os.path.dirname(
               get_package_share_directory('muriqui_description'))}
    world_file = os.path.join(
        get_package_share_directory('muriqui_gazebo'), 'worlds', 'empty_world.sdf')
    gui_config = os.path.join(
        get_package_share_directory('muriqui_gazebo'), 'gui', 'gui.config')
    # -r オプションで起動時にシミュレーションをスタートしないと、コントローラが起動しない
    ign_gazebo = ExecuteProcess(
            cmd=['ign gazebo -r', world_file, '--gui-config', gui_config],
            output='screen',
            additional_env=env,
            shell=True
        )

    ignition_spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=['-topic', '/robot_description',
                   '-name', 'muriqui',
                   '-z', '0.7',
                   '-allow_renaming', 'true',
                   '-topic', 'robot_description'],
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

    bridge_file = os.path.join(
        get_package_share_directory('muriqui_gazebo'), 'launch', 'bridge.yaml')

    bridge = Node(
                package='ros_gz_bridge',
                executable='parameter_bridge',
                parameters=[{'config_file': bridge_file, }],
                output='screen'
            )

    ld = LaunchDescription()
    ld.add_action(SetParameter(name='use_sim_time', value=True))
    ld.add_action(declare_use_head_camera)
    ld.add_action(declare_use_imu)
    ld.add_action(declare_arm_4joints)
    ld.add_action(declare_with_hand)
    ld.add_action(display_launch)
    ld.add_action(ign_gazebo)
    ld.add_action(ignition_spawn_entity)
    ld.add_action(spawn_joint_state_broadcaster)
    ld.add_action(spawn_right_arm_controller)
    ld.add_action(spawn_right_leg_controller)
    ld.add_action(spawn_left_arm_controller)
    ld.add_action(spawn_left_leg_controller)
    ld.add_action(spawn_neck_controller)
    ld.add_action(bridge)
    return ld
