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
import os
from pathlib import Path

from typing import Tuple, List

parser = argparse.ArgumentParser(
    description="Script that reads bram data via UART and does some evalutation on it."
)
parser.add_argument(
    "-d", "--device", help="Serial number of device.", default="210183A89AC3"
)
parser.add_argument(
    "-s",
    "--show_device",
    help="Show currently connected ftdi devices. NOTE: Devices occupied by Vivados Hardware Manager may not be available.",
    required=False,
    action="store_true",
)
parser.add_argument(
    "-v",
    "--previous_value",
    help="Value that was previously written to the BRAM (before it was depowered). Either ff or 00",
    default="00",
)
parser.add_argument(
    "-o", "--output_path", help="Path where read output files shall be saved"
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


def evaluate_readout(data: str, previous_value: str) -> List[Tuple[str, int]]:
    if len(previous_value) != 2:
        raise Exception("Wrong length of expected data. Please enter two hex digits")
    return [
        (data[i : i + 2], i / 2)
        for i in range(0, len(data), 2)
        if data[i : i + 2] != previous_value
    ]


def find_transmission_start(port) -> Tuple[bytes, bytes]:
    # Write anything to reset device state
    # -> Necessary because the received data is sometimes bugged after partial reconfig
    port.write(b"\x00")

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


def prepare_paths(input_path: str) -> Tuple[Path, Path]:
    """
    Expects path of form: .../1
    Returns: (.../data_reads/1, .../parity_reads/1
    """
    given_path = Path(input_path)
    base_path = Path(*given_path.parts[:-1])
    new_paths = (Path(base_path, "data_reads"), Path(base_path, "parity_reads"))

    file_name = given_path.parts[-1]
    for path in new_paths:
        if path.exists():
            continue
        else:
            path.mkdir(parents=True)

    return (Path(path, file_name) for path in new_paths)


if __name__ == "__main__":
    args = vars(parser.parse_args())

    if args["show_device"]:
        devices = pyftdi.ftdi.Ftdi.list_devices()
        print("Devices:")
        for dev in devices:
            print(f"\t{dev[0].description}: {dev[0].sn}")
        exit(0)

    if args["device"] is not None:
        # port = pyftdi.serialext.serial_for_url('ftdi://ftdi:2232:210183A89AC3/2 ', baudrate=9600, parity=serial.PARITY_EVEN)
        if args["device"] in ["A503VSXV", "A503VYYY", "A503VSBM"]:
            # This specific UART Adapter uses a different ftdi chip and port than dev boards
            # Making this more 'generic' could be a future TODO
            port = pyftdi.serialext.serial_for_url(
                f'ftdi://ftdi:232r:{args["device"]}/1',
                baudrate=115200,
                parity=serial.PARITY_NONE,
            )
        else:
            port = pyftdi.serialext.serial_for_url(
                f'ftdi://ftdi:2232:{args["device"]}/2',
                baudrate=115200,
                parity=serial.PARITY_NONE,
            )

        data, temp_parity = find_transmission_start(port)
        parity = temp_parity.hex()[1]
        header = None
        while True:
            temp_data, temp_parity, header = read_batch(port)

            if header != b"\x00\x00;":  # and b";" in header:
                data += temp_data
                parity += temp_parity.hex()[1]
            else:
                break

        parity = "".join([parity[i + 1] + parity[i] for i in range(0, len(parity), 2)])

        if args["output_path"] is not None:
            data_path, parity_path = prepare_paths(args["output_path"])

            with open(data_path, mode="wb") as f:
                f.write(data)
            with open(parity_path, mode="wb") as f:
                f.write(bytes.fromhex(parity))

    else:
        print(
            "No Serial Number specified. Call with '-s' to see possible serial numbers."
        )
