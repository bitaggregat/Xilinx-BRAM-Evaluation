import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import argparse
import os
from typing import List
from pathlib import Path

def add_to_bin_list(bin_list: List[int], measurement: bytes) -> None:
    """
    Parameter
    ---------
        bin_list: List for histogram where index is bin and element of said index is count
        measurement: byte sequence of one BRAM measurement (data and parity bits should be treated separately)
    """
    if len(bin_list) != len(measurement) * 8:
        raise Exception(
            "Error: Bit count of measurement has to be same as length of bin_list"
            f"Got bin_list of length {len(bin_list)}"
            f"and measurement of {len(measurement) * 8} bits.\n"
        )

    # Iterate through all bytes of measurement
    for idx, b in enumerate(measurement):
        # Turn integer b into 8 bit binary string
        bits_str = f"{b:8b}".replace(" ", "0")
        # Iterate through all bits of byte
        for idx2, bit in enumerate(bits_str):
            if bit == "1":
                bin_list[idx * 8 + idx2] += 1


def add_dir_to_bin_list(
    bin_list: List[int], path: str | Path, measurement_count: int
) -> None:
    """
    Parameters
    ---------
        path: Path to directory that contains measurement files
        measurement_count: Number of measurement files in directory
    """
    for i in range(measurement_count):
        with open(Path(path,str(i)), mode="rb") as f:
            read_bytes = f.read()
            add_to_bin_list(bin_list, read_bytes)


@ticker.FuncFormatter
def major_formatter(x, pos):
    """
    Removes "-" from plot labels
    Source: https://stackoverflow.com/a/51087117
    """
    label = str(-x) if x < 0 else str(x)
    return label


def create_histogram(
    bin_list: List[int],
    mode: str,
    bin_list2: List = None,
    display: bool = False,
    png_path: str | Path = None,
) -> None:
    """
    If bin_list and bin_list2 are provided, the following will be expected
    - bin_list == 0 to 1 flip measurement
    - bin_list2 == 1 to 0 flip measurement
    """
    xaxis = [i for i in range(len(bin_list))]

    plt.xlim(0, len(bin_list))
    fig, ax = plt.subplots()
    if mode == "0-to-1":
        ax.bar(xaxis, bin_list, color="g")
        plt.ylabel("Times bits flipped from 0 to 1", color="g")

    if mode == "1-to-0":
        ax.bar(xaxis, bin_list, color="b")
        plt.ylabel("Times bits flipped from 1 to 0", color="b")

    if mode == "both" and bin_list2 is not None:
        if len(bin_list) != len(bin_list2):
            raise Exception("Error: bin_list and bin_list2 have different lengths")
        else:
            ax.bar(xaxis, bin_list, color="g")
            ax.set_ylabel("Times bits flipped from 0 to 1", color="g")
            ax2 = ax.twinx()
            ax2.bar(xaxis, [-i for i in bin_list2], color="b")
            ax2.set_ylabel("Times bits flipped from 1 to 0", color="b")
            ax2.yaxis.set_major_formatter(major_formatter)
            ax.set_ylim(top=max(bin_list), bottom=-max(bin_list2))
            ax2.set_ylim(top=max(bin_list), bottom=-max(bin_list2))
            ax2.set_xlim(left=0,right=len(bin_list))
    ax.set_xlim(left=0,right=len(bin_list))
    plt.xlabel("Bit Index in BRAM")

    if display:
        plt.show()
    if png_path is not None:
        plt.savefig(png_path)


parser = argparse.ArgumentParser(
    description="Script that takes BRAM readout data (measurement)"
    " and shows the amount each bit address flipped in a histogram.\n"
)
parser.add_argument(
    "-o",
    "--output_file",
    help="Path where of plot png will be saved.\n"
    "When no path provided, plot will be displayed instead.",
)
parser.add_argument(
    "-pm",
    "--parity_mode",
    help="Type of measurement data that will be plotted. "
    "Mix will plot parity and data bits in a single plot",
    choices=["parity", "data", "mix"],
    required=True,
)
parser.add_argument(
    "-fm",
    "--flip_mode",
    help="Value of the BRAM previous to power reset. "
    "Use data where bits flipped from 0 to 1, 1 to 0 or plot both measurements in a single plot.",
    choices=["0-to-1", "1-to-0", "both"],
    required=True,
)
parser.add_argument(
    "-mb",
    "--multiple_blocks",
    help="Will expect '--path' to be a directory containing multiple BRAM directories."
    "e.g.:\n"
    "path\n"
    "L__BRAM_X16Y65_RAMB36_X2Y14\n"
    "|  L...\n"
    "L__BRAM_X16Y65_RAMB36_X2Y15\n"
    "|  L...\n"
    "L__...\n"
    "...\n",
    action="store_true",
    required=False,
)
parser.add_argument(
    "-c",
    "--count",
    help="Number of measurements that were done per BRAM Block",
    type=int,
    required=True,
)
parser.add_argument(
    "-p",
    "--path",
    help="Path to directory that contains the measurement files."
    "The following file structure is expected:\n\n"
    "path\n"
    "L__0-to-f\n"
    "|  L__data_reads\n"
    "|  |  |\n"
    "|  |  L__1\n"
    "|  |  L__2\n"
    "|  |  L__...\n"
    "|  L__parity_reads\n"
    "|     L__1\n"
    "|     L__2\n"
    "|     L__...\n"
    "L__f-to-0\n"
    "   L__data_reads\n"
    "   |  L__1\n"
    "   |  L__2\n"
    "   |  L__...\n"
    "   L__parity_reads\n"
    "      L__1\n"
    "      L__2\n"
    "      L__...\n",
    required=True,
)

if __name__ == "__main__":
    args = vars(parser.parse_args())

    parity_mode = args["parity_mode"]
    bin_list_dict = dict()

    if args["flip_mode"] == "both":
        flip_modes = ["0-to-1", "1-to-0"]
    else:
        flip_modes = args["flip_mode"]

    for fm in flip_modes:
        bin_list_dict[fm] = dict()
        if parity_mode == "parity" or parity_mode == "mix":
            bin_list_dict[fm]["parity"] = [0] * 4096
        if parity_mode == "data" or parity_mode == "mix":
            bin_list_dict[fm]["data"] = [0] * 4096 * 8

    # Get a list of all BRAM data directories if multiple bram reads are expected
    if args["multiple_blocks"]:
        bram_directories = [
            Path(args["path"], name)
            for name in os.listdir(args["path"])
            if os.path.isdir(Path(args["path"], name))
        ]
    # Put single bram directory into list
    # -> Less code duplicate in the sections that follow
    else:
        bram_directories = [args["path"]]

    for dir in bram_directories:
        # Fill bin list
        for flip_mode in bin_list_dict:
            for parity_mode in bin_list_dict[flip_mode]:
                add_dir_to_bin_list(
                    bin_list_dict[flip_mode][parity_mode],
                    Path(dir, flip_mode, parity_mode),
                    measurement_count=args["count"]
                )

    if parity_mode == "mix":
        # TODO mix parity and data bits
        exit(1)
    else:
        if len(bin_list_dict) == 2:
            create_histogram(
                bin_list_dict["0-to-1"][parity_mode],
                mode=args["flip_mode"],
                bin_list2=bin_list_dict["1-to-0"][parity_mode],
                display=args["output_file"] is None,
                png_path=args["output_file"]
            )
        else:
            create_histogram(
                bin_list_dict[bin_list_dict.keys()[0]][parity_mode],
                mode=args["flip_mode"],
                display=args["output_file"] is None,
                png_path=args["output_file"]
            )
        