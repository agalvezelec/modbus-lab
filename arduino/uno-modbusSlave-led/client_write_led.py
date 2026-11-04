import time
import logging
from pymodbus.client import ModbusSerialClient

# Configure logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)


def calculate_modbus_crc(data):
    """Calculate Modbus RTU CRC-16."""
    crc = 0xFFFF

    for byte in data:
        crc ^= byte

        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1

    return crc


def print_crc(crc):
    """Display CRC value and transmission byte order."""
    low_byte = crc & 0xFF
    high_byte = (crc >> 8) & 0xFF

    print(f"CRC-16: 0x{crc:04X}")
    print(f"CRC transmission order: {low_byte:02X} {high_byte:02X} (Low Byte first)")


def print_write_frame(dev_id, address, value):
    """Display Modbus RTU function 06 request frame."""

    frame = bytes([
        dev_id,
        0x06,
        (address >> 8) & 0xFF,
        address & 0xFF,
        (value >> 8) & 0xFF,
        value & 0xFF
    ])

    crc = calculate_modbus_crc(frame)

    print("\n[ WRITE REQUEST FRAME - FUNCTION 06 ]")
    print("-" * 65)
    print(f"| {'SLAVE ID':^10} | {'FUNCTION':^10} | {'REGISTER ADDRESS':^16} | {'VALUE':^10} |")
    print("-" * 65)
    print(
        f"| {dev_id:02X} (Hex)   | "
        f"06 (Hex)   | "
        f"{address:04X} (Hex)       | "
        f"{value:04X} (Hex)  |"
    )
    print("-" * 65)

    print("\n[ REQUEST CRC ]")
    print_crc(crc)


def control_led():

    print("\n==========================================")
    print("       PC MASTER CLIENT (SENDER PC)")
    print("             MODBUS RTU")
    print("==========================================")

    client = ModbusSerialClient(
        port="/dev/ttyACM0",
        baudrate=19200,
        bytesize=8,
        parity="N",
        stopbits=1,
        timeout=1
    )

    if not client.connect():
        print("\nError: Could not open the serial port.")
        return

    print("\nConnected to Modbus RTU bus.")

    dev_id = 1
    address = 0

    # ==========================================
    # 1. TURN ON LED (WRITE VALUE 1)
    # ==========================================

    print("\n[ LED CONTROL ]")
    print("Sending command: TURN ON LED (Value: 1)")

    print_write_frame(dev_id, address, 1)

    result = client.write_register(
        address=address,
        value=1,
        device_id=dev_id
    )

    if not result.isError():
        print("\nWrite operation successful.")
        print("LED STATUS: ON")
    else:
        print(f"\nWrite error: {result}")

        client.close()
        return

    # Wait 3 seconds to observe the physical LED
    print("\nWaiting 3 seconds...")
    time.sleep(3)

    # ==========================================
    # 2. TURN OFF LED (WRITE VALUE 0)
    # ==========================================

    print("\nSending command: TURN OFF LED (Value: 0)")

    print_write_frame(dev_id, address, 0)

    result = client.write_register(
        address=address,
        value=0,
        device_id=dev_id
    )

    if not result.isError():
        print("\nWrite operation successful.")
        print("LED STATUS: OFF")
    else:
        print(f"\nWrite error: {result}")

    # ==========================================
    # 3. CLOSE CONNECTION
    # ==========================================

    client.close()

    print("\nModbus RTU connection closed.")


if __name__ == "__main__":
    control_led()
