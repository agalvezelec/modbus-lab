import logging
from pymodbus.client import ModbusSerialClient

# Configure logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.WARNING)


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


def interactive_toggle():

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

    print("\nConnected to Modbus RTU bus (Interactive Mode).")
    print("Press [ENTER] to toggle the LED.")
    print("Type 'q' and press ENTER to exit.")

    dev_id = 1
    address = 0

    while True:

        user_input = input(
            "\nPress [ENTER] to toggle LED (or 'q' to exit): "
        )

        if user_input.lower() == 'q':
            break

        # ==========================================
        # 1. READ CURRENT LED STATE
        # ==========================================

        print("\n[ READ HOLDING REGISTER - REQUEST ]")

        read_frame = bytes([
            dev_id,
            0x03,
            (address >> 8) & 0xFF,
            address & 0xFF,
            0x00,
            0x01
        ])

        read_crc = calculate_modbus_crc(read_frame)

        print(f"Slave ID:       0x{dev_id:02X}")
        print("Function Code:  0x03 (Read Holding Registers)")
        print(f"Start Address:  0x{address:04X}")
        print("Quantity:       0x0001")

        print("\n[ REQUEST CRC ]")
        print_crc(read_crc)

        read_result = client.read_holding_registers(
            address=address,
            count=1,
            device_id=dev_id
        )

        if read_result.isError():
            print(f"\nRead error: {read_result}")
            continue

        current_value = read_result.registers[0]

        # ==========================================
        # 2. CALCULATE NEW LED STATE
        # ==========================================

        new_value = 0 if current_value > 0 else 1

        action_name = "TURN ON" if new_value == 1 else "TURN OFF"

        print("\n[ LED STATE ]")
        print(f"Current Arduino value: {current_value}")
        print(f"Requested action:      {action_name}")
        print(f"New register value:    {new_value}")

        # ==========================================
        # 3. WRITE NEW LED STATE
        # ==========================================

        print("\n[ WRITE SINGLE REGISTER - REQUEST ]")

        write_frame = bytes([
            dev_id,
            0x06,
            (address >> 8) & 0xFF,
            address & 0xFF,
            0x00,
            new_value
        ])

        write_crc = calculate_modbus_crc(write_frame)

        print(f"Slave ID:       0x{dev_id:02X}")
        print("Function Code:  0x06 (Write Single Register)")
        print(f"Register Address: 0x{address:04X}")
        print(f"Register Value:  0x{new_value:04X}")

        print("\n[ REQUEST CRC ]")
        print_crc(write_crc)

        write_result = client.write_register(
            address=address,
            value=new_value,
            device_id=dev_id
        )

        if not write_result.isError():

            print("\n[ WRITE RESPONSE - SLAVE -> MASTER ]")

            response_crc = calculate_modbus_crc(write_frame)

            print(f"Slave ID:       0x{dev_id:02X}")
            print("Function Code:  0x06")
            print(f"Register Address: 0x{address:04X}")
            print(f"Register Value:  0x{new_value:04X}")

            print("\n[ RESPONSE CRC ]")
            print_crc(response_crc)

            print("\nWrite operation successful.")
            print(f"LED STATUS: {'ON' if new_value == 1 else 'OFF'}")

        else:
            print(f"\nWrite error: {write_result}")

    client.close()

    print("\nModbus RTU connection closed.")


if __name__ == "__main__":
    interactive_toggle()
