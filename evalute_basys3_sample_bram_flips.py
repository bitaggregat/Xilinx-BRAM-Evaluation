from bitstream_handling.bs_handler import XC7BSHandler, remove_bram_init_packets
from bitstream_handling.position import XC7ElementPosition, SegBitPosition, XC7BitPosition
from bitstream_handling.fasm import TemplateFasmLeafFeature
from bitstream_handling.device import Basys3
from typing import Union
from pathlib import Path
import sys
import random


#elem_pos1 = XC7ElementPosition(19, 150, 20, 0x00C00000)
elem_pos2 = XC7ElementPosition(19, 150, 81, 0x00400300)


temp_ram18_y0_in_use = TemplateFasmLeafFeature.from_temp_str("BRAM_L.RAMB18_Y0.IN_USE 27_99 27_100")
temp_ram18_y1_in_use = TemplateFasmLeafFeature.from_temp_str("BRAM_L.RAMB18_Y1.IN_USE 27_220 27_221")

ram18_y0_in_use = temp_ram18_y0_in_use.to_fasm_leaf_feature(elem_pos2)
ram18_y1_in_use = temp_ram18_y1_in_use.to_fasm_leaf_feature(elem_pos2)


if __name__ == "__main__":
    in_bs_path = "bw_bram_wrap_partial.bit"#sys.argv[1]
    out_bs_path = "read_bram_modified.bit"#sys.argv[2]

    with open(in_bs_path, mode="rb") as f:
        bs_bytes =f.read()

        new_bitstream = remove_bram_init_packets( bs_bytes)

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
                "read_bram.bit",
                partial=False
        )

        with Basys3.from_available() as board:
            board.flash_bs_file_copenFPGALoader(
                "bw_return_0_partial.bit",
                partial=True
            )

        with open("temp", mode="wb") as tfile:
            tfile.write(new_bitstream)
        with Basys3.from_available() as board:
            board.flash_bs_bytes_copenFPGALoader(
                new_bitstream,
                partial=True
            )
        print("")

