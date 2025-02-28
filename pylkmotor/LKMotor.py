import can
from typing import Optional


class LKMotor:
    def __init__(self, bus_interface, bus_channel, motor_id, **kwargs):
        """Initialize the motor

        Args:
            bus_interface (str): CAN bus interface, e.g. "socketcan", "kvaser", "serial"
            bus_interface (str): CAN bus interface, e.g. "socketcan", "kvaser", "serial"
            bus_channel (str): CAN bus channel
            motor_id (int): Motor ID
            **kwargs: Additional arguments, e.g. baudrate, bitrate, etc.
            **kwargs: Additional arguments, e.g. baudrate, bitrate, etc.
        """

        self.motor_id = motor_id
        self.bus = can.interface.Bus(
            interface=bus_interface, channel=bus_channel, **kwargs
        )

        self.temperature = 0
        self.voltage = 0
        self.current = 0
        self.motor_state = 0
        self.error_state = 0
        self.iq = 0
        self.speed = 0
        self.multi_turn_angle = 0
        self.single_turn_angle = 0
        self.encoder_value = 0
        self.encoder_raw = 0
        self.encoder_offset = 0
        self.current_A = 0
        self.current_B = 0
        self.current_C = 0

    def _decimal_to_byte(self, value, digit):
        """Convert a decimal number to a byte list

        Args:
            value(int): Decimal number
            digit(int): Number of bytes

        Returns:
            list: Byte list, arranged from low to high
        """

        byte_list = []
        if value < 0:
            value -= 1 << digit * 8
        for i in range(digit):
            byte_list.append((value >> 8 * i) & 0xFF)

        return byte_list

    def _byte_to_decimal(self, values):
        """Convert a byte list to a decimal number

        Args:
            values(list): Byte list, arranged from low to high

        Returns:
            int: Decimal number
        """

        value_dec = 0
        for i in range(len(values)):
            value_dec += values[i] << 8 * i
        if values[-1] >> 7 == 1:
            value_dec -= 1 << len(values) * 8

        return value_dec

    def _send_command(self, command_byte, data=None):
        """Send a command to the motor

        Args:
            command_byte (uint8_t): Command byte
            data (unit8_t list): Data bytes to be sent
        """

        data = [command_byte] + (data if data else [0x00] * 7)
        message = can.Message(
            arbitration_id=0x140 + self.motor_id, data=data, is_extended_id=False
        )

        self.bus.send(message)
        print(f"Command sent to motor {self.motor_id} with data: {data}")

    def _receive_response(self, timeout=0.1):
        """Receive a response from the motor

        Args:
            timeout (float, optional): Timeout in seconds. Defaults to 0.1.

        Returns:
            list: Response data
        """
        response = self.bus.recv(timeout)
        if response is not None:
            return response.data
        return None

    def _parse_response_1(self, response):
        """Parse the response data from the motor

        This function updates:
        - Motor temperature (int8_t, 1 °C/LSB)
        - Motor voltage (int16_t, 0.01 V/LSB)
        - Motor current (int16_t, 0.01 A/LSB)
        - Motor state (uint8_t)
            | Byte | Description |
            |------|-------------|
            | 0x00 | Opened      |
            | 0x10 | Closed      |
        - Error state (uint8_t)
            | Bit |     Description    | 0 |              1                |
            |-----|--------------------|---|-------------------------------|
            |  0  | Low voltage        | 0 | Low voltage protection        |
            |  1  | High voltage       | 0 | High voltage protection       |
            |  2  | Driver temperature | 0 | Driver temperature over limit |
            |  3  | Motor temperature  | 0 | Motor temperature over limit  |
            |  4  | Current            | 0 | Over current                  |
            |  5  | Short circuit      | 0 | Short circuit                 |
            |  6  | Stall              | 0 | Stall                         |
            |  7  | Input signal       | 0 | Input signal timeout          |

        Args:
            response (list): Response data from the motor
        """

        if response:
            self.temperature = self._byte_to_decimal([response[1]])
            self.voltage = self._byte_to_decimal(response[2:4]) * 0.01
            self.current = self._byte_to_decimal(response[4:6]) * 0.01
            self.motor_state = response[6]
            self.error_state = response[7]
        return (
            self.temperature,
            self.voltage,
            self.current,
            self.motor_state,
            self.error_state,
        )

    def _parse_response_2(self, response):
        """Parse the response data from the motor

        This function updates:
        - Motor temperature (int8_t, 1 °C/LSB)
        - Motor iq (int16_t)
            | Model |     Unit      |
            |-------|---------------|
            | MF    | 33/4096 A/LSB |
            | MG    | 66/4096 A/LSB |
        - Motor speed (int16_t, 1 dps/LSB)
        - Encoder value (uint16_t)
            | Model |   Range   |
            |-------|-----------|
            | 14bit | 0 ~ 16383 |
            | 15bit | 0 ~ 32767 |
            | 16bit | 0 ~ 65535 |

        Args:
            response (list): Response data from the motor
        """

        if response:
            self.temperature = self._byte_to_decimal([response[1]])
            self.iq = self._byte_to_decimal(response[2:4])
            self.speed = self._byte_to_decimal(response[4:6])
            self.encoder_value = self._byte_to_decimal(response[6:8])
        return self.temperature, self.iq, self.speed, self.encoder_value

    def _parse_response_3(self, response):
        """Parse the response data from the motor

        This function updates:
        - Motor temperature (int8_t, 1 °C/LSB)
        - Phase A, B, C current (int16_t)
            | Model |     Unit      |
            |-------|---------------|
            | MF    | 33/4096 A/LSB |
            | MG    | 66/4096 A/LSB |

        Args:
            response (list): Response data from the motor
        """
        if response:
            self.temperature = self._byte_to_decimal([response[1]])
            self.current_A = self._byte_to_decimal(response[2:4])
            self.current_B = self._byte_to_decimal(response[4:6])
            self.current_C = self._byte_to_decimal(response[6:8])
        return self.temperature, self.current_A, self.current_B, self.current_C

    def read_motor_status_1(self):
        """Read the motor status 1

        This function sends a command to the motor to read the motor status including:
        - Motor temperature (int8_t, 1 °C/LSB)
        - Motor voltage (int16_t, 0.01 V/LSB)
        - Motor current (int16_t, 0.01 A/LSB)
        - Motor state (uint8_t)
        - Error state (uint8_t)
        Then the response data is parsed and the motor status is updated.
        """

        self._send_command(0x9A)
        response = self._receive_response()
        if response:
            return self._parse_response_1(response)

    def clear_error_flags(self):
        """Clear the error flags of the motor

        This function sends a command to the motor to clear the error flags.
        """

        self._send_command(0x9B)
        response = self._receive_response()
        if response:
            return self._parse_response_1(response)

    def read_motor_status_2(self):
        """Read the motor status 2

        This function sends a command to the motor to read the motor status including:
        - Motor temperature (int8_t, 1 °C/LSB)
        - Motor iq (int16_t)
        - Motor speed (int16_t, 1 dps/LSB)
        - Encoder value (uint16_t)
        Then the response data is parsed and the motor status is updated.
        """

        self._send_command(0x9C)
        response = self._receive_response()
        if response:
            return self._parse_response_2(response)

    def read_motor_status_3(self):
        """Read the motor status 3

        This function sends a command to the motor to read the motor status including:
        - Motor temperature (int8_t, 1 °C/LSB)
        - Phase A, B, C current (int16_t)
        Then the response data is parsed and the motor status is updated.
        """

        self._send_command(0x9D)
        response = self._receive_response()
        if response:
            return self._parse_response_3(response)

    def motor_shutdown(self):
        """Shutdown the motor

        This function sends a command to the motor to turn off the motor.
        It will clear the number of turns and previous commands.
        The LED light will shine slowly.
        The motor can receive and respond to the commands, but does not execute them.
        """

        self._send_command(0x80)
        return self._receive_response()

    def motor_run(self):
        """Start the motor

        This function sends a command to the motor to start the motor.
        The LED light will keep on.
        The motor can receive commands and execute them.
        """

        self._send_command(0x88)
        return self._receive_response()

    def motor_stop(self):
        """Stop the motor

        This function sends a command to the motor to stop the motor.
        The state of the motor will not be cleared.
        The motor can receive new commands and execute them.
        """

        self._send_command(0x81)
        return self._receive_response()

    def brake_control(self, control_byte):
        """Brake control command

        This function sends a command to the motor to control the brake.

        Args:
            control_byte (uint8_t): Control byte, 0x00 for brake, 0x01 for release, 0x10 for state
        """

        data = self._decimal_to_byte(control_byte, 1) + [0x00] * 6
        self._send_command(0x8C, data)
        response = self._receive_response()
        if response:
            return self._byte_to_decimal([response[1]])

    def open_loop_control(self, power_control):
        """Open loop control command

        This function sends a command to the motor to control the motor in open loop.
        Only realized on MS series motors.

        Args:
            power_control (int16_t): Power control, range from -850 to 850
        """

        data = [0x00] * 3 + self._decimal_to_byte(power_control, 2) + [0x00] * 2
        self._send_command(0xA0, data)
        response = self._receive_response()
        if response:
            return self._parse_response_2(response)

    def torque_loop_control(self, iq_control):
        """Torque loop control command

        This function sends a command to the motor to control the motor in torque loop.
        Only realized on MF, MH, and MG series motors.
        The iq range for MF series is -16.5 ~ 16.5 A, and for MG series is -33 ~ 33 A.

        Args:
            iq_control (int16_t): Torque control, range from -2048 to 2048
        """

        data = [0x00] * 3 + self._decimal_to_byte(iq_control, 2) + [0x00] * 2
        self._send_command(0xA1, data)
        response = self._receive_response()
        if response:
            return self._parse_response_2(response)

    def speed_loop_control(self, iq_control, speed_control):
        """Speed loop control command

        This function sends a command to the motor to control the motor in speed loop.

        Args:
            iq_control (int16_t): Torque control, range from -2048 to 2048
            speed_control (int32_t): Speed control, unit: 0.01 dps/LSB
        """

        data = (
            [0x00]
            + self._decimal_to_byte(iq_control, 2)
            + self._decimal_to_byte(speed_control, 4)
        )
        self._send_command(0xA2, data)
        response = self._receive_response()
        if response:
            return self._parse_response_2(response)

    def multi_turn_position_control(
        self, angle_control, max_speed: Optional[int] = None
    ):
        """Multi-turn position control command

        This function sends a command to the motor to control the motor in multi-turn position loop.

        Args:
            angle_control (int32_t): Angle control, unit: 0.01 degree/LSB
            max_speed (uint16_t, optional): Maximum speed, unit: 1 dps/LSB
        """

        if max_speed is None:
            data = [0x00] * 3 + self._decimal_to_byte(angle_control, 4)
            self._send_command(0xA3, data)
        else:
            data = (
                [0x00]
                + self._decimal_to_byte(max_speed, 2)
                + self._decimal_to_byte(angle_control, 4)
            )
            self._send_command(0xA4, data)
        response = self._receive_response()
        if response:
            return self._parse_response_2(response)

    def single_turn_position_control(
        self, spin_direction, angle_control, max_speed: Optional[int] = None
    ):
        """Single-turn position control command

        This function sends a command to the motor to control the motor in single-turn position loop.

        Args:
            spin_direction (uint8_t): Spin direction, 0x00 for clockwise, 0x01 for counterclockwise
            angle_control (int32_t): Angle control, unit: 0.01 degree/LSB
            max_speed (uint16_t, optional): Maximum speed, unit: 1 dps/LSB
        """

        if max_speed is None:
            data = (
                self._decimal_to_byte(spin_direction, 1)
                + [0x00] * 2
                + self._decimal_to_byte(angle_control, 4)
            )
            self._send_command(0xA5, data)
        else:
            data = (
                self._decimal_to_byte(spin_direction, 1)
                + self._decimal_to_byte(max_speed, 2)
                + self._decimal_to_byte(angle_control, 4)
            )
            self._send_command(0xA6, data)
        response = self._receive_response()
        if response:
            return self._parse_response_2(response)

    def incremental_position_control(
        self, angle_increment, max_speed: Optional[int] = None
    ):
        """Incremental position control command

        This function sends a command to the motor to control the motor in incremental position loop.

        Args:
            angle_increment (int32_t): Angle increment, unit: 0.01 degree/LSB
            max_speed (uint16_t, optional): Maximum speed, unit: 1 dps/LSB
        """

        if max_speed is None:
            data = [0x00] * 3 + self._decimal_to_byte(angle_increment, 4)
            self._send_command(0xA7, data)
        else:
            data = (
                [0x00]
                + self._decimal_to_byte(max_speed, 2)
                + self._decimal_to_byte(angle_increment, 4)
            )
            self._send_command(0xA8, data)
        response = self._receive_response()
        if response:
            return self._parse_response_2(response)

    def read_control_params(self):
        """Read control parameter command

        This function sends a command to the motor to read the control parameter.

        Returns:
            list: Control parameter data
        """

        self._send_command(0xC0)
        return self._receive_response()

    def write_control_params(self, control_param_id, param_bytes):
        """Write control parameter command

        This function sends a command to the motor to write the control parameter.

        Args:
            control_param_id (uint8_t): Control parameter ID
            param_bytes (list): Parameter bytes
        """

        data = [0xC1, control_param_id] + param_bytes
        self._send_command(0xC1, data)
        return self._receive_response()

    def read_encoder_data(self):
        """Read encoder data command

        This function sends a command to the motor to read the encoder data.

        Returns:
            encoder_value (uint16_t): Encoder value
            encoder_raw (uint16_t): Raw encoder value
            encoder_offset (uint16_t): Encoder offset
        """

        self._send_command(0x90)
        response = self._receive_response()
        if response:
            self.encoder_value = self._byte_to_decimal(response[2:4])
            self.encoder_raw = self._byte_to_decimal(response[4:6])
            self.encoder_offset = self._byte_to_decimal(response[6:8])
        return self.encoder_value, self.encoder_raw, self.encoder_offset

    def set_zero_position(self):
        """Set the current position as the zero position

        This function sends a command to the motor to set the current position as the zero position.
        Note: the encoder offset will be updated until the motor is restarted.
        Warning: this command will effect the lifetime of the driver, do not use it frequently.

        Returns:
            encoder_offset (int16_t): Encoder offset
        """
        self._send_command(0x19)
        response = self._receive_response()
        if response:
            self.encoder_offset = self._byte_to_decimal(response[6:8])
        return self.encoder_offset

    def read_multi_turn_angle(self):
        """Read the multi-turn angle

        This function sends a command to the motor to read the multi-turn angle.

        Returns:
            multi_turn_angle (int64_t): Multi-turn angle, unit: 0.01 degree/LSB
        """

        self._send_command(0x92)
        response = self._receive_response()
        if response:
            self.multi_turn_angle = self._byte_to_decimal(response[1:8])
        return self.multi_turn_angle

    def read_single_turn_angle(self):
        """Read the single-turn angle

        This function sends a command to the motor to read the single-turn angle.

        Returns:
            single_turn_angle (uint32_t): Single-turn angle, range from 0 to 35999
        """

        self._send_command(0x94)
        response = self._receive_response()
        if response:
            self.single_turn_angle = self._byte_to_decimal(response[4:8])
        return self.single_turn_angle

    def set_position_to_angle(self, multi_turn_angle):
        """Set the current position as a multi-turn angle

        Args:
            motor_angle (int): Target angle, unit: 0.01 degree/LSB
        """

        data = [0x00] * 3 + self._decimal_to_byte(multi_turn_angle, 4)
        self._send_command(0x95, data)
        return self._receive_response()


if __name__ == "__main__":
    motor = LKMotor(bus_interface="socketcan", bus_channel="can0", motor_id=1)

    status_1 = motor.read_motor_status_1()
    print(f"Motor status 1: {status_1}")
