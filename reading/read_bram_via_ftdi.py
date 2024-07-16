#!/usr/bin/env python3
"""
- Script that reads bram via uart from a xilinx fpga.
- Is supposed to be used in combination with uart bram implementation in (TODO link)
-
"""

import pyftdi.serialext
import pyftdi.ftdi
import serial
import argparse

from typing import Tuple

parser = argparse.ArgumentParser(
    description="Script that reads bram data via UART and does some evalutation on it."
)
parser.add_argument("-d", "--device", help="Serial number of device.")
parser.add_argument(
    "-s",
    "--show_device",
    help="Show currently connected ftdi devices. NOTE: Devices occupied by Vivados Hardware Manager may not be available.",
    required=False,
    action="store_true",
)
# Start byte/ byte swap?
#


# dev =  pyftdi.ftdi.Ftdi.list_devices()
# ftdi://ftdi:2232:210183A89AC3/2 -> Basys3
# ftdi://ftdi:2232:210279651642/2 -> Zybo


read_finished = False
start = False
bram_size = 8192
counter = 0
synchro = False
check_puf = False


def find_transmission_start(port) -> Tuple[bytes, bytes]:
    last_two_bytes = [None, None]
    while True:
        temp_byte = port.read(1)

        if temp_byte == b";" and last_two_bytes == [b"\x00", b"\x00"]:
            # Found start
            data = port.read(4)
            parity = port.read(1)

            return data, parity
        else:
            last_two_bytes.pop(0)
            last_two_bytes.append(temp_byte)


def read_batch(port) -> Tuple[bytes, bytes, bytes]:
    header = port.read(3)
    data = port.read(4)
    parity = port.read(1)
    return data, parity, header


if __name__ == "__main__":
    args = vars(parser.parse_args())

    if args["show_device"]:
        devices = pyftdi.ftdi.Ftdi.list_devices()
        print("Devices:")
        for dev in devices:
            print(f"\t{dev[0].description}: {dev[0].sn}")

    if args["device"] is not None:
        # port = pyftdi.serialext.serial_for_url('ftdi://ftdi:2232:210183A89AC3/2 ', baudrate=9600, parity=serial.PARITY_EVEN)
        port = pyftdi.serialext.serial_for_url(
            f'ftdi://ftdi:2232:{args["device"]}/2',
            baudrate=9600,
            parity=serial.PARITY_EVEN,
        )

        data, temp_parity = find_transmission_start(port)
        parity = temp_parity.hex()[1]
        header = None
        while True:
            temp_data, temp_parity, header = read_batch(port)

            if header != b"\x00\x00;" and b";" in header:
                data += temp_data
                parity += temp_parity.hex()[1]
            else:
                break

        print(data)
        parity = "".join([parity[i + 1] + parity[i] for i in range(0, len(parity), 2)])
        print(bytes.fromhex(parity))
        print(len(data))
    else:
        print(
            "No Serial Number specified. Call with '-s' to see possible serial numbers."
        )
