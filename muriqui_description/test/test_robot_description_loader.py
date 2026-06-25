# Copyright 2024 RT Corporation

from muriqui_description.robot_description_loader import RobotDescriptionLoader
from launch.launch_context import LaunchContext
import pytest


def exec_load(loader):
    # Reference:
    # https://github.com/ros2/launch/blob/074cd2903ddccd61bce8f40a0f58da0b7c200481/launch/test/launch/substitutions/test_command.py#L47
    context = LaunchContext()
    return loader.load().perform(context)


def test_load_description():
    # Expect that xacro loading is successful
    rdl = RobotDescriptionLoader()
    assert exec_load(rdl)


def test_change_description_path():
    # Expect that xacro loading is failed
    rdl = RobotDescriptionLoader()
    rdl.robot_description_path = 'hoge'
    with pytest.raises(Exception) as e:
        exec_load(rdl)
    assert e.value


def test_feet_fsr():
    # Expect that xacro loading is successful
    rdl = RobotDescriptionLoader()
    rdl.feet_fsr = 'false'
    assert 'fsr_r_front_right_joint' not in exec_load(rdl)

    rdl.feet_fsr = 'true'
    assert 'fsr_r_front_right_joint' in exec_load(rdl)


def test_arm_4joints():
    rdl = RobotDescriptionLoader()
    rdl.arm_4joints = 'true'
    assert 'Arm_R_Link2_Upper' in exec_load(rdl)
    assert 'Arm_R_Link2_Lower' in exec_load(rdl)
    assert 'Arm_L_Link2_Upper' in exec_load(rdl)
    assert 'Arm_L_Link2_Lower' in exec_load(rdl)
    assert '"Arm_R_Link2"' not in exec_load(rdl)
    assert '"Arm_L_Link2"' not in exec_load(rdl)

    rdl.arm_4joints = 'false'
    assert 'Arm_R_Link2_Upper' not in exec_load(rdl)
    assert 'Arm_R_Link2_Lower' not in exec_load(rdl)
    assert 'Arm_L_Link2_Upper' not in exec_load(rdl)
    assert 'Arm_L_Link2_Lower' not in exec_load(rdl)
    assert 'Arm_R_Link2' in exec_load(rdl)
    assert 'Arm_L_Link2' in exec_load(rdl)


def test_with_hand():
    rdl = RobotDescriptionLoader()
    rdl.with_hand = 'true'
    assert 'Arm_R_Link3_Hand' in exec_load(rdl)
    assert 'Arm_L_Link3_Hand' in exec_load(rdl)
    assert 'Arm_R_Link_Finger' in exec_load(rdl)
    assert 'Arm_L_Link_Finger' in exec_load(rdl)
    assert '"Arm_R_Link3"' not in exec_load(rdl)
    assert '"Arm_L_Link3"' not in exec_load(rdl)

    rdl.with_hand = 'false'
    assert 'Arm_R_Link3_Hand' not in exec_load(rdl)
    assert 'Arm_L_Link3_Hand' not in exec_load(rdl)
    assert 'Arm_R_Link_Finger' not in exec_load(rdl)
    assert 'Arm_L_Link_Finger' not in exec_load(rdl)
    assert '"Arm_R_Link3"' in exec_load(rdl)
    assert '"Arm_L_Link3"' in exec_load(rdl)


def test_camera_d435i():
    rdl = RobotDescriptionLoader()
    rdl.camera_d435i = 'true'
    assert 'Head_D435i.stl' in exec_load(rdl)

    rdl.camera_d435i = 'false'
    assert 'Head_D435i.stl' not in exec_load(rdl)


def test_camera_d405():
    rdl = RobotDescriptionLoader()
    rdl.camera_d405 = 'true'
    assert 'Head_D405.stl' in exec_load(rdl)

    rdl.camera_d405 = 'false'
    assert 'Head_D405.stl' not in exec_load(rdl)
