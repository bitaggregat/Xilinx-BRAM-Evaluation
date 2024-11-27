from bitstream_handling.bs_handler import remove_bram_init_packets
import argparse


parser = argparse.ArgumentParser(
    description="Script that takes "
    "partial BRAM initialization input bitstream, "
    "then modifies said bitstream such that the BRAM "
    "will be initialized but without defined values"
)
parser.add_argument(
    "-pb",
    "--bram_partial_bs",
    help="Path to partial Bitstream that initializes "
    "a BRAM block in a region of the FPGA."
    "The partial bitstream is tied to another full bitstream "
    "that initalizes the FPGA with"
    " a communication interface and connects said interface to the BRAM block",
    required=True,
)
parser.add_argument(
    "-ob",
    "--output_partial_bs",
    help="Path where the output bitstream of this script shall be saved."
    "The output is a .bin file (headless bitstream)",
    required=True,
)
parser.add_argument(
    "-a",
    "--first_bram_frame_address",
    help="Address of the first frame with bram content as hex string. "
    "This can vary depending on the region the partial design is located in.\n"
    "-Can be looked up by calling this script with '-s'.\n"
    "Pass 'heuristic' in order to let the script decide "
    "which address is the bram batch frame address\n"
    "ATTENTION: It is recommended to use '-s' "
    "to verify when using 'heuristic'",
    default="heuristic",
)
parser.add_argument(
    "-ar",
    "--architecture",
    help="Xilinx FPGA architecture used.",
    choices=["XC7", "XCUS+"],
)
parser.add_argument(
    "-s",
    "--show_address_candidates",
    help="Shows all FAR write value. One of them can then be used as '-a'",
    action="store_true",
)

if __name__ == "__main__":
    # Transfer args to variables (redundant..., but makes refactoring easier)
    args = vars(parser.parse_args())
    output_partial_bs = args["output_partial_bs"]
    bram_partial_bs = args["bram_partial_bs"]
    base_bram_addr = args["first_bram_frame_address"]
    architecture = args["architecture"]
    show_address_candidates = args["show_address_candidates"]

    with open(bram_partial_bs, mode="rb") as f:
        bs_bytes = f.read()

        if show_address_candidates and base_bram_addr is None:
            base_bram_addr = "ffffffff"

        modified_bs_bytes = remove_bram_init_packets(
            bs_bytes,
            base_bram_addr,
            arch=architecture,
            use_header=False,
            show=show_address_candidates,
        )
        with open(output_partial_bs, mode="wb") as out_file:
            out_file.write(modified_bs_bytes)
