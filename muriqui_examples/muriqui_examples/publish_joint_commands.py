#!/usr/bin/env python3
# coding: UTF-8

# Copyright 2024 RT Corporation

import argparse
import pandas as pd
import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from sensor_msgs.msg import JointState
import time
import threading
from std_msgs.msg import Float64MultiArray


class JointCommandsPublisher(Node):
    def __init__(self):
        super().__init__('joint_commands_publisher')

        self._joint_state = JointState()
        self._has_joint_state = False

        self._commands_publishers = {}
        self._commands_publishers['right_arm'] = self.create_publisher(
            Float64MultiArray, '/right_arm_controller/commands', 10)
        self._commands_publishers['left_arm'] = self.create_publisher(
            Float64MultiArray, '/left_arm_controller/commands', 10)
        self._commands_publishers['right_leg'] = self.create_publisher(
            Float64MultiArray, '/right_leg_controller/commands', 10)
        self._commands_publishers['left_leg'] = self.create_publisher(
            Float64MultiArray, '/left_leg_controller/commands', 10)
        self._commands_publishers['neck'] = self.create_publisher(
            Float64MultiArray, '/neck_controller/commands', 10)

        self._joint_targets = None
        self._goal_configs = None

        def joint_state_callback(msg):
            self._joint_state = msg
            self._has_joint_state = True
        self._sub_joint_state = self.create_subscription(
            JointState, 'joint_states', joint_state_callback, 10)

    def has_joint_state(self) -> bool:
        return self._has_joint_state

    def load_csv(self, filepath) -> bool:
        try:
            self._joint_targets = pd.read_csv(filepath)

        except Exception as e:
            self.get_logger().error(f"Failed to load CSV file: {e}")
            return False

        if not self.has_joint_state():
            self.get_logger().error("Joint state is not available.")
            self.get_logger().error("Please wait for joint state update before loading CSV file.")
            return False

        self._extract_config()

        if not self._joint_targets_have_valid_group() or\
           not self._joint_targets_have_valid_joint():
            return False

        return True

    def get_goal_names(self) -> list[str]:
        # Do not use pd.DataFrame.columns.difference() to keep the order of columns.
        exclude_columns = ['group', 'joint']
        return [col for col in self._joint_targets.columns if col not in exclude_columns]

    def publish_present_positions_repeatedly(self, timeout: float) -> None:
        # Publish present positions of all joints.
        present_positions = self._extract_present_positions_by_group()

        start_time = time.time()
        while time.time() - start_time < timeout:
            for group_name in self._joint_targets['group'].unique():
                self._publish_joint_commands(group_name, present_positions[group_name])
            time.sleep(0.1)

    def move_to(self, goal_name: str) -> None:
        # Move all joints from present positions to goal positions defined in CSV file.

        start_positions = self._extract_present_positions_by_group()
        goal_positions = self._extract_goal_positions_by_group(goal_name)
        duration = self._get_config_value('DURATION', goal_name)
        DT = self._get_config_value('DT', goal_name)

        total_elapsed_time = self._get_config_value('TIME_OFFSET', goal_name)
        while total_elapsed_time < duration:
            step_start_time = time.time()
            fraction = total_elapsed_time / duration

            for group_name in self._joint_targets['group'].unique():
                eased_positions = [
                    start + (goal - start) * fraction
                    for start, goal in zip(start_positions[group_name], goal_positions[group_name])
                ]
                self._publish_joint_commands(group_name, eased_positions)

            step_elapsed_time = time.time() - step_start_time
            sleep_time = max(0, DT - step_elapsed_time)
            total_elapsed_time += sleep_time
            time.sleep(sleep_time)

    def _extract_config(self):
        # Extract goal configurations from joint_targets.
        self._goal_configs = self._joint_targets[
            self._joint_targets['group'] == 'CONFIG'].drop(columns='group').reset_index(drop=True)
        self._joint_targets = self._joint_targets.drop(self._goal_configs.index)

    def _get_config_value(self, config_name, goal_name) -> float:
        return self._goal_configs.loc[
            self._goal_configs['joint'] == config_name, goal_name].values[0]

    def _joint_targets_have_valid_group(self) -> bool:
        unique_groups = self._joint_targets['group'].unique()
        publisher_names = set(self._commands_publishers.keys())

        # Check if all unique groups are included in publisher_names
        invalid_groups = [group for group in unique_groups if group not in publisher_names]

        if invalid_groups:
            self.get_logger().error(f"Invalid group name in CSV file: {invalid_groups}")
            return False
        return True

    def _joint_targets_have_valid_joint(self) -> bool:
        joint_names = set(self._joint_state.name)

        # Check if all joint targets are included in joint_names
        invalid_joints = [
            joint for joint in self._joint_targets['joint'] if joint not in joint_names
        ]

        if invalid_joints:
            self.get_logger().error(f"Invalid joint name in CSV file: {invalid_joints}")
            return False
        return True

    def _extract_present_positions(self, joint_names: list[str]) -> list[float]:
        joint_positions = []
        for joint_name in joint_names:
            idx = self._joint_state.name.index(joint_name)
            joint_positions.append(self._joint_state.position[idx])
        return joint_positions

    def _extract_present_positions_by_group(self) -> dict[str, list[float]]:
        positions: dict[str, list[float]] = {}
        for group_name, group in self._joint_targets.groupby('group'):
            joint_names = group['joint']
            positions[group_name] = self._extract_present_positions(joint_names)
        return positions

    def _extract_goal_positions_by_group(self, goal_name: str) -> dict[str, list[float]]:
        positions: dict[str, list[float]] = {}
        for group_name, group in self._joint_targets.groupby('group'):
            positions[group_name] = group[goal_name].to_list()
        return positions

    def _publish_joint_commands(self, group_name: str, joint_positions: list[float]) -> None:
        msg = Float64MultiArray()
        msg.data = joint_positions
        self._commands_publishers[group_name].publish(msg)


def wait_for_joint_state_update(timeout: float) -> bool:
    start_time = time.time()
    while time.time() - start_time < timeout:
        if node.has_joint_state():
            return True
        time.sleep(0.1)
    return False


def main() -> None:
    logger.info("Wait for Joint State")
    if not wait_for_joint_state_update(5):
        logger.warn("Timeout")
        return

    if not node.load_csv(args.csv_filepath):
        logger.error("Failed to load CSV file.")
        return

    # Publish present positions of all joints to establish stable communication.
    node.publish_present_positions_repeatedly(2.0)

    for goal_name in node.get_goal_names():
        logger.info("goal_name: " + goal_name)
        node.move_to(goal_name)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '--csv_filepath',
        default='path/to/joint_goals.csv',
        type=str, help='Path to joint goals CSV file')

    # Exclude ROS-specific arguments
    args, other_args = arg_parser.parse_known_args()
    rclpy.init(args=other_args)

    node = JointCommandsPublisher()
    executor = MultiThreadedExecutor()
    executor.add_node(node)

    # Spin the node in the background
    executor_thread = threading.Thread(target=executor.spin, daemon=True)
    executor_thread.start()

    logger = rclpy.logging.get_logger('example')

    try:
        main()
    except KeyboardInterrupt:
        pass

    executor.shutdown()
    rclpy.shutdown()
