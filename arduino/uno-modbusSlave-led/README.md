## Arduino UNO – Modbus RTU Slave LED Control

An Arduino UNO connected to the PC via USB operates as a Modbus RTU Slave. The PC acts as the Modbus Master, allowing the user to control the onboard LED directly from the terminal using Python and PyModbus.

The example demonstrates Modbus RTU communication, register reading and writing, and LED state control. It also displays the Modbus request and response information, including CRC-16 calculations, for communication testing and debugging.

**Original Arduino library:**

https://github.com/smarmengol/Modbus-Master-Slave-for-Arduino

### Requirements

- Arduino UNO
- USB connection to the PC
- Python 3.12 or later
- `uv` package manager
- Arduino CLI

### Installation and execution

Move the library into the Arduino libraries directory:

```bash
# Install the Modbus library
# Place Modbus-Master-Slave-for-Arduino in:
# ~/Arduino/libraries/
```

Compile the Arduino sketch:

```bash
arduino-cli compile -b arduino:avr:uno uno-modbusSlave-led.ino
```

Upload the firmware:

```bash
arduino-cli upload -b arduino:avr:uno -p /dev/ttyACM0 uno-modbusSlave-led.ino
```

Run the Python Modbus Master client:

```bash
uv sync
```

Toggle the onboard LED:

```bash
uv run client_toggle_led.py
```

Alternatively, execute the automatic LED test:

```bash
uv run client_write_led.py
```

### Modbus RTU Configuration

| Parameter | Value |
|---|---|
| Device | Arduino UNO |
| PC role | Modbus Master |
| Arduino role | Modbus Slave |
| Slave ID | 1 |
| Baud rate | 19200 |
| Data bits | 8 |
| Parity | None |
| Stop bits | 1 |
| Serial port | `/dev/ttyACM0` |
| Register address | 0 |
| Read function | 0x03 |
| Write function | 0x06 |

**Note:** The onboard LED is controlled by writing `1` (ON) or `0` (OFF) to holding register 0.
