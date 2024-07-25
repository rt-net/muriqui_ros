# Copyright 2024 RT Corporation

from muriqui_hardware.muriqui_comm import MuriquiComm


def gen_serial_mock(mocker):
    mock_serial_constructor = mocker.patch('serial.Serial', autospec=True)
    return mock_serial_constructor.return_value


def set_mock_read(mock_serial, data: bytes):
    mock_serial.in_waiting = len(data)

    def mock_read(size):
        mock_serial.in_waiting = 0
        return data

    mock_serial.read.side_effect = mock_read


def test_initial_value(mocker):
    gen_serial_mock(mocker)
    comm = MuriquiComm('/dev/ttyACM0', 115200)
    assert comm.button_state == {}
    assert comm.voltages == {}


def test_read_valid_data(mocker):
    mock_serial = gen_serial_mock(mocker)
    comm = MuriquiComm('/dev/ttyACM0', 115200)

    set_mock_read(mock_serial, b'START,SW0:1,SW1:0,SW2:1,VCC:12.3,END')
    assert comm.read() is True
    assert comm.button_state == {"SW0": True, "SW1": False, "SW2": True}
    assert comm.voltages == {"VCC": 12.3}


def test_read_invalid_data(mocker):
    mock_serial = gen_serial_mock(mocker)
    comm = MuriquiComm('/dev/ttyACM0', 115200)

    set_mock_read(mock_serial, b'ART,SW0:1,SW1:0,SW2:1,VCC:12.3,END')
    assert comm.read() is False
    assert comm.button_state == {}
    assert comm.voltages == {}


def test_repeat_reading(mocker):
    mock_serial = gen_serial_mock(mocker)
    comm = MuriquiComm('/dev/ttyACM0', 115200)

    set_mock_read(mock_serial, b'START,SW0:1,SW1:0,SW2:1,VCC:12.3,END')
    assert comm.read() is True

    set_mock_read(mock_serial, b'START,SW0:0,SW1:1,SW2:0,VCC:9.8,END')
    assert comm.read() is True
    assert comm.button_state == {"SW0": False, "SW1": True, "SW2": False}
    assert comm.voltages == {"VCC": 9.8}


def test_read_splitted_data(mocker):
    mock_serial = gen_serial_mock(mocker)
    comm = MuriquiComm('/dev/ttyACM0', 115200)

    set_mock_read(mock_serial, b'VCC:12.3,END\r\nSTART,SW0:1,SW1:1,SW')
    assert comm.read() is False

    set_mock_read(mock_serial, b'2:1,VCC:3.4,END')
    assert comm.read() is True
    assert comm.button_state == {"SW0": True, "SW1": True, "SW2": True}
    assert comm.voltages == {"VCC": 3.4}


def test_read_multiple_data(mocker):
    mock_serial = gen_serial_mock(mocker)
    comm = MuriquiComm('/dev/ttyACM0', 115200)

    set_mock_read(
        mock_serial,
        b'START,SW0:1,SW1:0,SW2:1,VCC:12.3,END\r\nSTART,SW0:0,SW1:1,SW2:0,VCC:9.8,END')
    assert comm.read() is True
    assert comm.button_state == {"SW0": False, "SW1": True, "SW2": False}
    assert comm.voltages == {"VCC": 9.8}


def test_write_commands(mocker):
    mock_serial = gen_serial_mock(mocker)
    comm = MuriquiComm('/dev/ttyACM0', 115200)

    comm.write_commands(False, False, False)
    mock_serial.write.assert_called_with(b'000')

    comm.write_commands(True, False, True)
    mock_serial.write.assert_called_with(b'101')

    comm.write_commands(False, True, False)
    mock_serial.write.assert_called_with(b'010')
