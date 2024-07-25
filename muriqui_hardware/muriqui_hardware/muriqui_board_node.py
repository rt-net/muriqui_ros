#!/usr/bin/env python3
# coding: UTF-8

# Copyright 2024 RT Corporation

from muriqui_hardware.muriqui_comm import MuriquiComm
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from muriqui_msgs.msg import ButtonState
from muriqui_msgs.msg import LedControl
from muriqui_msgs.msg import Voltages


class MuriquiBoard(Node):
    def __init__(self):
        super().__init__('muriqui_board')

        self.declare_parameter("port", "/dev/muriqui_board")
        self.declare_parameter("baudrate", 115200)
        self._comm = MuriquiComm(
            self.get_parameter("port").value, self.get_parameter("baudrate").value)

        self._pub_buttons = self.create_publisher(
            ButtonState, 'muriqui_buttons', 10)

        self._pub_voltages = self.create_publisher(
            Voltages, 'muriqui_voltages', 10)

        def leds_callback(msg):
            self._comm.write_commands(msg.led0_on, msg.led1_on, msg.led2_on)

        self._sub_leds = self.create_subscription(
            LedControl, 'muriqui_leds', leds_callback, 10)

        self._timer = self.create_timer(0.1, self._timer_callback)

    def _timer_callback(self) -> None:
        if self._comm.read() is False:
            return

        button_state_msg = ButtonState()
        button_state_msg.button0_pressed = self._comm.button_state.get("SW0", False)
        button_state_msg.button1_pressed = self._comm.button_state.get("SW1", False)
        button_state_msg.button2_pressed = self._comm.button_state.get("SW2", False)
        self._pub_buttons.publish(button_state_msg)

        voltages_msg = Voltages()
        voltages_msg.motor_power = self._comm.voltages.get("VCC", 0.0)
        self._pub_voltages.publish(voltages_msg)


def main(args=None):
    rclpy.init(args=args)
    node = MuriquiBoard()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()
