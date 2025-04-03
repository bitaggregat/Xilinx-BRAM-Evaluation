import argparse
import enum
from pathlib import Path
from typing import Any

import h5py

import hdf5_wrapper.experiment_hdf5

class DataSetting(enum.Enum):
    PBLOCK_WISE = enum.auto()
    HALF_PBLOCK_WISE = enum.auto()
    SEPARATE_STRIPES = enum.auto()


def parse_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Transform measurement data from bram start-up values " \
        "and converts them s.t. they are usable with NIST tests."
    )
    parser.add_argument(
        "-i", "--input_hdf5",
        help="hdf5 file that containing experiment data to " \
        "manage by this script",
        type=Path
    )
    parser.add_argument(
        "-s", "--setting",
        help="Describes how the data is distributed within the dataset",
        choices=[setting.name for setting in DataSetting],
    )
    parser.add_argument(
        "-g", "--groupe_pblocks_by",
        help="Allows to groupe data of pblocks by clock region." \
        "Only predefined groupes (matching the pblocks distribution " \
        "among clock regions in the hardware configurations) can be selected",
        choices=["None", "zu1eg"],
        default="None",
        required=False
    )
    parser.add_argument(
        "-o", "--output_file",
        help="Path to NIST dataset file that shall be created",
        type=Path
    )
    args = vars(parser.parse_args())
    args["setting"] = DataSetting[args["setting"]]
    return args

def pblock_groupes(groupe_setting: str) -> list[list[str]]:
    """
    Returns pblocks grouped by clock region (based on hardware design)
    """
    match groupe_setting:
        case "None":
            return []
        case "zu1eg":
            # The order of these pblocks on the grid wasn't thought through
            # Which is why this list looks inconsistent.
            return [f"pblock_{i}" for i in [4, 5, 6]] + \
                [f"pblock_{i}" for i in [1, 2, 3]] + \
                [f"pblock_{i}" for i in [9, 8, 7]]
            
        case _:
            raise Exception(
                "This shouldn't happen. " \
                "Somehow an invalid groupe setting got through"
            )

def y_index_from_bram_name(bram_name: str) -> str:
    return int(bram_name.split("Y")[-1])

def separate_stripes(data: bytes) -> tuple[bytes, bytes]:

    first_stripe = b''
    second_stripe = b''

    if len(data) != 4096:
        raise Exception(
            f"Start-up value data," 
            f"has length {len(data)} instead of 4096. Why?"
        )

    for i in range(0, 4096, 16):
        first_stripe += data[i:i+4] + data[i+12:i+16]
        second_stripe += data[i+4:i+12]
    
    return first_stripe, second_stripe

def select_data(
        data_setting: DataSetting, 
        experiment: hdf5_wrapper.Experiment,
        groupe_setting: str
    ) -> bytes:
    print("a")
    groupe_setting = pblock_groupes(groupe_setting)


    if groupe_setting:
        pblock_order = groupe_setting
    else:
        # If something with multiple boards has to be implemented, do it here
        pblock_order = sorted(list(
            list(
                experiment.subcontainers.values()
                )[0].subcontainers.keys()
        ))
    print(pblock_order)

    result_blob = b''
    for pblock_name in pblock_order:
        pblock = list(
            experiment.subcontainers.values())[0].subcontainers[pblock_name]
        bram_order = sorted(
            list(pblock.subcontainers.keys()), key=y_index_from_bram_name
        )
        if len(bram_order) != 12:
            raise Exception(
                f"Expected 12 brams in {pblock_name},"
                f" but found {len(bram_order)}."
            )

        if data_setting is DataSetting.HALF_PBLOCK_WISE:
            bram_order = bram_order[:6]

        pblock_data = b''
        stripe_1 = b''
        stripe_2 = b''
        for bram_name in bram_order:
            bram = pblock.subcontainers[bram_name]
            data = bram.read_sessions[bram.read_session_names[0]].data_reads[0].raw_read

            if data_setting is DataSetting.SEPARATE_STRIPES:
                stripe_1_part, stripe_2_part = separate_stripes(data)
                stripe_1 += stripe_1_part
                stripe_2 += stripe_2_part
            else:
                pblock_data += data

        if data_setting is DataSetting.SEPARATE_STRIPES:
            pblock_data += stripe_1 + stripe_2

        result_blob += pblock_data
    return result_blob
    
        
def main(args: Any) -> None:
    
    with h5py.File(args["input_hdf5"], "r") as f:
        print("start")
        experiment = hdf5_wrapper.Experiment.from_hdf5(
            f, commit=f.attrs["commit"]
        )
        print("help")
        created_data = select_data(
            args["setting"], 
            experiment, 
            args["groupe_pblocks_by"]
        )
        with open(args["output_file"], mode="wb") as f2:
            f2.write(created_data)
        
if __name__ == "__main__":
    args = parse_args()
    main(args)