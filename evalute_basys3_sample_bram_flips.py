from bitstream_handling.bs_handler import XC7BSHandler, remove_bram_init_packets
from bitstream_handling.position import XC7ElementPosition, SegBitPosition, XC7BitPosition
from bitstream_handling.fasm import TemplateFasmLeafFeature
from bitstream_handling.device import Basys3
from typing import Union
from pathlib import Path
import sys
import random


def initialize_bram(bram_frame_batch_start_addr: str, base_bs: str|Path, bramless_partial_bs: str|Path, bram_partial_bs: str|Path) -> None:

    # Open partial bitstream that will be manipulated
    with open(bram_partial_bs, mode="rb") as f:
        bs_bytes =f.read()

        new_bitstream = remove_bram_init_packets(bs_bytes, bram_frame_batch_start_addr)


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

    with Basys3.from_available() as board:
        board.flash_bs_file_copenFPGALoader(
            base_bs,
            partial=False
    )

    with Basys3.from_available() as board:
        board.flash_bs_file_copenFPGALoader(
            bramless_partial_bs,
            partial=True
        )

    with open("temp", mode="wb") as tfile:
        tfile.write(new_bitstream)
    with Basys3.from_available() as board:
        board.flash_bs_bytes_copenFPGALoader(
            new_bitstream,
            partial=True
        )


if __name__ == "__main__":
    # TODO better argparsing

    base_bs = sys.argv[1]
    bramless_partial_bs = sys.argv[2]
    bram_partial_bs = sys.argv[3]
