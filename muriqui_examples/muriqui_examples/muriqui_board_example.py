#!/usr/bin/env python3
# coding: UTF-8

# Copyright 2024 RT Corporation

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from muriqui_msgs.msg import ButtonState
from muriqui_msgs.msg import LedControl
from muriqui_msgs.msg import Voltages


class MuriquiBoardExample(Node):
    def __init__(self):
        super().__init__('muriqui_board_example')

        self._pub_leds = self.create_publisher(
            LedControl, 'muriqui_leds', 10)

        def buttons_callback(msg):
            self.get_logger().info(f"Button0: {msg.button0_pressed}")
            self.get_logger().info(f"Button1: {msg.button1_pressed}")
            self.get_logger().info(f"Button2: {msg.button2_pressed}")

            leds_msg = LedControl()
            leds_msg.led0_on = msg.button0_pressed
            leds_msg.led1_on = msg.button1_pressed
            leds_msg.led2_on = msg.button2_pressed
            self._pub_leds.publish(leds_msg)

        def voltages_callback(msg):
            self.get_logger().info(f"Motor Power voltages is: {msg.motor_power:.1f}")
            if msg.motor_power < 10.0:
                self.get_logger().warn("Motor power is too low!")

        self._sub_buttons = self.create_subscription(
            ButtonState, 'muriqui_buttons', buttons_callback, 10)

        self._sub_voltages = self.create_subscription(
            Voltages, 'muriqui_voltages', voltages_callback, 10)


def main(args=None):
    rclpy.init(args=args)
    node = MuriquiBoardExample()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()
