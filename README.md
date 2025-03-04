# pyLKMotor: Control the LK motor with Python

[![PyPI version](https://img.shields.io/pypi/v/pylkmotor.svg?logo=pypi&logoColor=white)](https://pypi.org/project/pylkmotor/)
[![Python versions](https://img.shields.io/pypi/pyversions/pylkmotor.svg?logo=python&logoColor=white)](https://pypi.org/project/pylkmotor/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

## Description

PyLKMotor is a Python library to control the [LK motor](http://www.lkmotor.cn). It provides a simple interface to control the motor and read its status. The library supports:

- Enable/Disable the motor
- Torque loop control
- Speed loop control
- Multi-turn, single-turn, and incremental position control
- Read/write motor parameters
- Read encoder data, multi-turn and single-turn position
- Set zero position

## Hardware Requirements

To use this library, you need the following hardware:

- LK motor
- CAN bus interface
- 24V power supply

Note that this library uses the CAN bus interface to communicate with the motor. You need to connect the motor to the CAN bus interface and power supply. We tested the library with SocketCAN on Linux, and USB-to-CAN adapters on Windows. More details for supported CAN bus interfaces can be found in the [python-can](https://python-can.readthedocs.io/en/stable/interfaces.html) library.

## Installation

The `pylkmotor` library supports `Python>=3.10`, tested on Windows 11, Ubuntu 22.04, and Raspberry Pi OS (bookworm). It can be installed using pip:

```bash
pip install pylkmotor
```

Or you can install it from the source code:

```bash
git clone https://github.com/han-xudong/pyLKMotor.git
cd pyLKMotor
pip install .
```

## Usage

Here is an example to initialize the motor:

```python
from pylkmotor import LKMotor

motor = LKMotor(bus_interface={BUS_INTERFACE}, bus_channel={BUS_CHANNEL}, motor_id={MOTOR_ID}, **kwargs)
```

- `bus_interface`: The CAN bus interface, e.g., `socketcan`, `kvaser`, `serial`, etc.
- `bus_channel`: The CAN bus channel, e.g., `can0`, `can1`, etc.
- `motor_id`: The motor ID, e.g., `1`, `2`, etc.
- `kwargs`: The keyword arguments to initialize the CAN bus interface, e.g., `baudrate`, etc.

This depends on the CAN bus interface you are using. For example, if you are using the `socketcan` interface, you can initialize the motor as follows:

```python
motor = LKMotor(bus_interface='socketcan', bus_channel='can0', motor_id=1)
```

If you are using a USB-to-CAN adapter, you can initialize the motor as follows:

```python
motor = LKMotor(bus_interface='serial', bus_channel='COM3', motor_id=1, baudrate=1000000)
```

And here are some functions provided to control the motor:

- `read_motor_status_1()`: Read the motor status 1, including the motor temperature, motor voltage, motor current, motor state, and error state.

```python
status_1 = motor.read_motor_status_1()
print(status_1)
```

- `read_motor_status_2()`: Read the motor status 2, including the motor temperature, motor iq, motor speed, and encoder value.

```python
status_2 = motor.read_motor_status_2()
print(status_2)
```

- `read_motor_status_3()`: Read the motor status 3, including the motor temperature, and phase current.

```python
status_3 = motor.read_motor_status_3()
print(status_3)
```

- `clear_error_flags()`: Clear the error flags.

```python
motor.clear_error_flags()
```

- `motor_shutdown`: Shutdown the motor. The motor can receive and respond to the commands, but does not execute them.

```python
motor.motor_shutdown()
```

- `motor_run()`: Start the motor. When the motor is powered on, the default state is running. The motor can receive commands and execute them.

```python
motor.motor_run()
```

- `motor_stop()`: Stop the motor. The motor can receive new commands and execute them.

```python
motor.motor_stop()
```

- `brake_control()`: Control the motor brake. `0x00` is to enable the brake, `0x01` is to disable the brake, `0x10` is to read the brake status.

```python
motor.brake_control(0x00)
```

- `open_loop_control()`: Control the motor in the open-loop mode. This is only for MS series motors. `power_control` is `int16_t`, ranging from `-850` to `850`.

```python
motor.open_loop_control(power_control={POWER_CONTROL})
```

- `torque_loop_control()`: Control the motor in the torque loop mode. This is for MF, MH and MG series motors. `iq_control` is `int16_t`, ranging from `-2048` to `2048`.

```python
motor.torque_loop_control(iq_control={IQ_CONTROL})
```

- `speed_loop_control()`: Control the motor in the speed loop mode. `iq_control` is `int16_t`, ranging from `-2048` to `2048`, and `speed_control` is `int32_t` with the unit of `0.01 dps/LSB`.

```python
motor.speed_loop_control(iq_control={IQ_CONTROL}, speed_control={SPEED_CONTROL})
```

- `multi_turn_position_control()`: Control the motor in the multi-turn position control mode. `angle_control` is `int32_t` with the unit of `0.01 degree/LSB`, and `max_speed` is `uint16_t (optional)` with the unit of `1 dps/LSB`.

```python
motor.multi_turn_position_control(angle_control={ANGLE_CONTROL}, max_speed=(OPTIONAL){MAX_SPEED})
```

- `single_turn_position_control()`: Control the motor in the single-turn position control mode. `spin_direction` is `uint8_t`,  where `0x00` is clockwise, and `0x01` is counterclockwise. `angle_control` is `int16_t` with the unit of `0.01 degree/LSB`, and `max_speed` is `uint16_t (optional)` with the unit of `1 dps/LSB`.

```python
motor.single_turn_position_control(spin_direction={SPIN_DIRECTION}, angle_control={ANGLE_CONTROL}, max_speed=(OPTIONAL){MAX_SPEED})
```

- `incremental_position_control()`: Control the motor in the incremental position control mode. `angle_increment` is `int32_t` with the unit of `0.01 degree/LSB`, and `max_speed` is `uint16_t (optional)` with the unit of `1 dps/LSB`.

```python
motor.incremental_position_control(angle_increment={ANGLE_INCREMENT}, max_speed=(OPTIONAL){MAX_SPEED})
```

- `read_control_params()`: Read the control parameters.

```python
control_params = motor.read_control_params()
print(control_params)
```

- `write_control_params()`: Write the control parameters. `control_params_id` is `uint8_t`, ranging from `0` to `3`, and `param_bytes` is `uint8_t[8]`.

```python
motor.write_control_params(control_params_id={CONTROL_PARAMS_ID}, param_bytes={PARAM_BYTES})
```

- `read_encoder_data()`: Read the encoder data. `encoder_value` is the encoder absolute value, which is the raw value minus the offset. `encoder_raw` is the raw encoder value. `encoder_offset` is the encoder offset, which refers to the zero position.

```python
encoder_value, encoder_raw, encoder_offset = motor.read_encoder_data()
print(encoder_value, encoder_raw, encoder_offset)
```

- `set_zero_position()`: Set the zero position. The current position will be set as the zero position.

```python
encoder_offset = motor.set_zero_position()
print(encoder_offset)
```

- `read_multi_turn_angle()`: Read the multi-turn angle. `multi_turn_angle` is `int64_t` with the unit of `0.01 degree/LSB`. The positive value is clockwise, and the negative value is counterclockwise.

```python
multi_turn_angle = motor.read_multi_turn_angle()
print(multi_turn_angle)
```

- `read_single_turn_angle()`: Read the single-turn angle. `single_turn_angle` is `unit32_t` with the unit of `0.01 degree/LSB`. The value increases from the zero position clockwise, ranging from `0` to `359999`.

```python
single_turn_angle = motor.read_single_turn_angle()
print(single_turn_angle)
```

- `set_position_to_angle()`: Set the current position as a multi-turn angle. `multi_turn_angle` is `int32_t` with the unit of `0.01 degree/LSB`.

```python
motor.set_position_to_angle(multi_turn_angle={MULTI_TURN_ANGLE})
```

## License

PyLKMotor is released under the [MIT License](LICENSE).

## Acknowledgement

- [LK Motor](http://www.lkmotor.cn): The manufacturer of the LK motor, providing the [CAN protocol](docs/can_protocol.pdf).
- [python-can](https://python-can.readthedocs.io/en/stable/): A Python library to control the CAN bus interface.
