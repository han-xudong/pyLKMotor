# pyLKMotor: Control the LK motor with Python

[![PyPI version](https://img.shields.io/pypi/v/pylkmotor.svg?logo=pypi&logoColor=white)](https://pypi.org/project/pylkmotor/)
[![Python versions](https://img.shields.io/pypi/pyversions/pylkmotor.svg?logo=python&logoColor=white)](https://pypi.org/project/pylkmotor/)
[![Github](https://img.shields.io/badge/Github-pyLKMotor-purple.svg?logo=github&logoColor=white)](https://github.com/han-xudong/pyLKMotor)
[![Tutorial](https://img.shields.io/badge/Tutorial-pyLKMotor-purple.svg?logo=read-the-docs&logoColor=white)](https://github.com/han-xudong/pyLKMotor/blob/main/docs/tutorial.ipynb)
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

This depends on the CAN bus interface you are using.

After initializing the motor, you can control the motor following the [tutorial](https://github.com/han-xudong/pyLKMotor/blob/main/docs/tutorial.ipynb).

## Resources

In `docs/`, you can find the following resources:

- `can_protocol.pdf`: The CAN protocol document provided by LK Motor.
- `LK_motor_tool_v2.35.exe`: The LK motor tool to configure the motor parameters.

## License

PyLKMotor is released under the [MIT License](LICENSE).

## Acknowledgement

- [LK Motor](http://www.lkmotor.cn): The manufacturer of the LK motor, providing the [CAN protocol](docs/can_protocol.pdf).
- [python-can](https://python-can.readthedocs.io/en/stable/): A Python library to control the CAN bus interface.
