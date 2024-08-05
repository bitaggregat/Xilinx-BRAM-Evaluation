from bitstream_handling.bs_handler import XC7BSHandler, remove_bram_init_packets
from bitstream_handling.position import (
    XC7ElementPosition,
    SegBitPosition,
    XC7BitPosition,
)
from bitstream_handling.fasm import TemplateFasmLeafFeature
from bitstream_handling.device import Basys3
from typing import Union
from pathlib import Path
import sys
import random
import argparse
import time

parser = argparse.ArgumentParser(
    description="Script that takes an three input bitstreams, then initializes FPGA for BRAM experiment, measure."
)

parser.add_argument(
    "-nb",
    "--bramless_bs",
    help="Path to partial bramless Bitstream file that initializes Target Region with a design that does not use BRAM blocks.\n"
    "This cuts the power to the previously initiated BRAM Block(s)",
    required=True,
)
parser.add_argument(
    "-fb",
    "--bram_full_bs",
    help="Path to Bitstream file that initializes Target Region with a design that uses BRAM blocks, initializes their values "
    "and initializes a communication interface/protocol IP in another region of the FPGA.\n"
    "This cuts the power to the previously initiated BRAM Block(s)",
    required=True,
)
parser.add_argument(
    "-pb",
    "--bram_partial_bs",
    help='Partial version of "bram_full_bs" (path to partial bitstream).'
    'NOTE: BOTH "--bram_full_bs" AND "--bram_partial_bs" are required.',
    required=True,
)
parser.add_argument(
    "-a",
    "--first_bram_frame_address",
    help="Address of the first frame with bram content as hex string. This can vary depending on the region the partial design is located in.\n"
    "-Can be looked up by unpacking '--bram_partial_bs'.\n"
    "-Will be >= 00c00000 (usually 00c00080 or 00c00000)",
    default="00c00080",
)
parser.add_argument(
    "-t",
    "--wait_time",
    help="Time that will be waited for while bram is depowered in seconds.\n"
    "Note: Having the bram depowered for longer may enhance results.",
    type=int,
    default=0,
)


def initialize_bram(
    bram_frame_batch_start_addr: str,
    base_bs: str | Path,
    bramless_partial_bs: str | Path,
    bram_partial_bs: str | Path,
    wait_time: int = 0,
) -> None:
    # Open partial bitstream that will be manipulated
    with open(bram_partial_bs, mode="rb") as f:
        bs_bytes = f.read()

        # Create modified partial bitstream (
        # BS will connect bram to power but doesn't reinitialize bram with values
        new_bitstream = remove_bram_init_packets(bs_bytes, bram_frame_batch_start_addr, arch="XC7")

        # bsh = XC7BSHandler.from_bytes(bs_bytes, "basys3_part.json")
        # relevant_frames = [
        #     frame
        #     for frame in bsh.frames
        #     if
        #     #(frame.addr >= 0x00400300 and frame.addr <= (0x00400300 + 28))
        #     #or
        #     frame.addr < 0x00C00000
        #     #any([pos.frame_addr == frame.addr for pos in ram18_y0_in_use.positions + ram18_y1_in_use.positions])
        # ]

        # with open("basys3_part.json") as js:
        #     json_content = "\n".join(js.readlines())
        # bsh.setup(json_content, {})

        # bsh.evo_frames = [frame for frame in bsh.frames if frame.addr < 0x00C00000]

        # bsh.evo_frame_dict = {frame.addr: frame for frame in bsh.evo_frames}

        # with open(out_bs_path, mode="wb") as f2:
        #     f2.write(bsh.partial_evo_bytes())

    # Flash full bitstream
    # Initializes FPGA with communication interface and bram
    with Basys3.from_available() as board:
        board.flash_bs_file_copenFPGALoader(base_bs, partial=False)

    # Flash temporary partial design that doesn't use bram
    # This cuts the power from the bram
    with Basys3.from_available() as board:
        board.flash_bs_file_copenFPGALoader(bramless_partial_bs, partial=True)

    # Let some time pass before bram is reenabled
    time.sleep(wait_time)

    # with open("temp", mode="wb") as tfile:
    #    tfile.write(new_bitstream)

    # Increase number of flashing procedures for different results
    for _ in range(1):
        # Flash modified partial bs
        # This will connect BRAM to power again
        # But it will not initiate the BRAM with values
        with Basys3.from_available() as board:
            board.flash_bs_bytes_copenFPGALoader(new_bitstream, partial=True)


if __name__ == "__main__":

    # Transfer args to variables (kinda redundant..., but makes refactoring easier)
    args = vars(parser.parse_args())
    bram_full_bs = args["bram_full_bs"]
    bramless_partial_bs = args["bramless_bs"]
    bram_partial_bs = args["bram_partial_bs"]
    base_bram_addr = args["first_bram_frame_address"]
    wait_time = args["wait_time"]
    print("Note this script supports currently only the basys3")

    initialize_bram(
        base_bram_addr,
        base_bs=bram_full_bs,
        bramless_partial_bs=bramless_partial_bs,
        bram_partial_bs=bram_partial_bs,
        wait_time=wait_time,
    )
