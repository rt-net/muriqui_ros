# Copyright 2024 RT Corporation

import re
import serial


class MuriquiComm:
    HEADER = 'START'
    FOOTER = 'END'

    def __init__(self, port, baudrate):
        self._serial = serial.Serial(port, baudrate, timeout=3, write_timeout=3)
        self._buffer = ''
        self._button_state: dict[str, bool] = {}
        self._voltages: dict[str, float] = {}

    def __del__(self):
        self._serial.close()

    def read(self) -> bool:
        # Read all available data from the serial port
        if self._serial.in_waiting > 0:
            self._buffer += self._serial.read(self._serial.in_waiting).decode('utf-8')

        # Split the buffer into string list by comma, carriage return, and newline
        parts = re.split('[,\r\n]', self._buffer)
        complete_data = self._extract_complete_data_from_last(parts)

        if complete_data:
            self._decode(complete_data)
            self._buffer = ''
            return True
        return False

    def write_commands(self, led0=False, led1=False, led2=False) -> None:
        write_data = f'{int(led0)}{int(led1)}{int(led2)}'
        self._serial.write(write_data.encode('utf-8'))

    @property
    def button_state(self) -> dict[str, bool]:
        return self._button_state

    @property
    def voltages(self) -> dict[str, float]:
        return self._voltages

    def _extract_complete_data_from_last(self, parts: list[str]) -> list[str]:
        # Invert the list to get the last part first
        reversed_parts = parts[::-1]
        recording = False
        segment = []
        for part in reversed_parts:
            if part == self.FOOTER:
                recording = True

            if recording:
                segment.append(part)

            if part == self.HEADER and recording:
                return segment[::-1]
        return []

    def _decode(self, data: list[str]) -> None:
        for d in data:
            if 'SW' in d:
                key, state = d.split(':')
                self._button_state[key] = bool(int(state))
            elif 'V' in d:
                key, value = d.split(':')
                self._voltages[key] = float(value)
