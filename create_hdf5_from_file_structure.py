import h5py
from pathlib import Path
from typing import Dict
import json
import datetime
import argparse
import numpy as np

# General:
# Sometimes experiments may fail and/or are interrupted
# This could lead to an incomplete file structure
# We therefore do not assume that all subconstituents of
#   a BRAM experiment are always available


def add_meta_data(parent: h5py.Group, meta_data: Dict[str, str]) -> None:
    """
    Adds relevant meta data to hdf5 groupe
    """
    for key, value in meta_data.items():
        parent.attrs[key] = value


def add_meta_data_from_json(parent: h5py.Group, json_path: Path) -> None:
    """
    Loads meta data from a json file
    Saves meta data as attributes of parent group
    """
    with open(json_path, mode="r") as f:
        json_dict = json.load(f)
        add_meta_data(parent, json_dict)


def add_temperature_dataset(temperature_file: Path, parent: h5py.Group) -> None:
    """
    Adds temperature data set to <bram_name>/<0-to-f or f-to-0> group

    Parameters:
        temperature_file: Path to temperature.txt file
        parent: Parent group of dataset
    """

    with open(temperature_file, mode="r") as f:
        # Zynq FPGAs will have two temperature sensors (PL and PS)
        # We assume the first output to be the temperature of PL
        values = [
            float(measurement.split()[0].strip()) for measurement in f.readlines()
        ]

        parent.create_dataset("temperature", (len(values),), dtype="f", data=values)


def add_bram_dataset(path: Path, parent: h5py.Group, dataset_name: str) -> None:
    """
    Adds bram reads as a dataset to group

    Parameters:
        path: Path to directory that contains multiple bram reads
        parent: Parent group of dataset
        name: Name of the dataset (should be either "data" or "parity")
    """
    # Sort files numerically ascending: [0, 1, 2, ..., 10, ...]
    # This is done to avoid: [0, 1, 10, 100, 1000, 2, 20,...]
    files_sorted_by_index = sorted(
        [file_path for file_path in path.iterdir() if file_path.is_file()],
        key=lambda x: int(x.stem),
    )

    read_data = []
    for file in files_sorted_by_index:
        with open(file, mode="rb") as f:
            read_data.append(f.read())
    seq_length = len(read_data[0])

    # Quality control
    assert all([len(read) == seq_length for read in read_data])

    parent.create_dataset(
        dataset_name,
        (len(read_data),),
        dtype=np.void(read_data).dtype,
        data=np.void(read_data),
    )


def add_bram_dataset_group(path: Path, parent: h5py.Group, group_name: str) -> None:
    """
    Adds multiple datasets based on content in "previous_value_00" or "previous_value_ff" dir

    Parameters:
        path: Path to directory that contains dirs parity and data
        parent: Parent group of dataset
        name: Name of the group (should be either "previous_value_00" or "previous_value_ff")
    """
    bram_data_group = parent.create_group(group_name)

    # Add parity dataset if available
    parity_path = Path(path, "parity_reads")
    if parity_path.exists() and parity_path.is_dir():
        add_bram_dataset(parity_path, bram_data_group, "parity_reads")

    # Add data dataset if available
    data_path = Path(path, "data_reads")
    if data_path.exists() and data_path.is_dir():
        add_bram_dataset(data_path, bram_data_group, "data_reads")

    # Add temperature if available
    temperature_path = Path(path, "temperature.txt")
    if temperature_path.exists() and temperature_path.is_file():
        add_temperature_dataset(temperature_path, bram_data_group)


def add_bitstream_group(path: Path, parent: h5py.Group) -> None:
    bs_files = [file_path for file_path in path.iterdir() if file_path.is_file()]

    bitstream_group = parent.create_group("bitstreams", track_order=True)

    # Add five bitstreams as attributes
    for bs in bs_files:
        match bs.stem.split("_"):
            case [*_, "partial", "bram", "bs"]:
                with open(bs, mode="rb") as f:
                    bitstream_group.attrs["partial_bram_bs"] = np.void(f.read())
            case [*_, "modified", "partial"]:
                with open(bs, mode="rb") as f:
                    bitstream_group.attrs["modified_partial"] = np.void(f.read())
            case [*_, "ff"]:
                with open(bs, mode="rb") as f:
                    bitstream_group.attrs["ff"] = np.void(f.read())
            case [*_, "00"]:
                with open(bs, mode="rb") as f:
                    bitstream_group.attrs["00"] = np.void(f.read())
            case [*_, "bramless", "partial"]:
                with open(bs, mode="rb") as f:
                    bitstream_group.attrs["bramless_partial"] = np.void(f.read())


def add_bram_group(path: Path, parent: h5py.Group) -> None:
    """
    Adds measurement Data from single BRAM experiment as path to a given parent group
    - Adds measurements with previous value ff and 00 if available)
    - Also adds bitstreams if available

    Parameters:
        path: Path to BRAM measurements in (Linux)filesystem
        parent: Parent group of new group
    """

    bram_name = path.parts[-1]

    bram_group = parent.create_group(bram_name)

    sub_paths = [p for p in path.iterdir() if p.parts[-1] != "bs"]
    for expected_path in sub_paths:
        if expected_path.exists() and expected_path.is_dir():
            add_bram_dataset_group(expected_path, bram_group, expected_path.parts[-1])

    bs_path = Path(path, "bs")
    if bs_path.exists() and bs_path.is_dir():
        add_bitstream_group(bs_path, bram_group)


def add_pblock_group(path: Path, parent: h5py.Group) -> None:
    """
    Adds all bram data directories from a given pblock directory
    """

    pblock_name = path.parts[-1]
    pblock_group = parent.create_group(pblock_name)

    bram_dirs = [
        sub_path
        for sub_path in path.iterdir()
        if sub_path.is_dir() and "RAMB" in sub_path.parts[-1]
    ]

    for bram_dir in bram_dirs:
        add_bram_group(bram_dir, pblock_group)


def add_single_board_group(path: Path, parent: h5py.Group) -> None:
    """
    Adds content of a board directory
    """
    board_group = parent.create_group(path.parts[-1])

    # Add meta data from expected json file
    meta_data_json_path = Path(path, "meta_data.json")
    if meta_data_json_path.exists() and meta_data_json_path.is_file():
        add_meta_data_from_json(board_group, meta_data_json_path)

    # Iterate through all pblocks in given base directory
    pblock_dirs = [
        sub_path
        for sub_path in path.iterdir()
        if sub_path.is_dir() and "pblock" in sub_path.parts[-1]
    ]

    for pblock_dir in pblock_dirs:
        add_pblock_group(pblock_dir, board_group)


def add_boards_group(path: Path, parent: h5py.Group) -> None:
    """
    Adds all board directories from a given boards directory
    """
    boards_group = parent.create_group("boards")

    board_dirs = [sub_path for sub_path in path.iterdir() if sub_path.is_dir()]

    for board_dir in board_dirs:
        add_single_board_group(board_dir, boards_group)


def derivate_read_session_names(hdf5_file: h5py.Group) -> None:
    """
    Parameters:
        hdf5_file: File AFTER experiment data has been written to it
                   (after add_boards_group has already been called)
    """
    read_session_names = [
        read_session
        for read_session in list(
            list(list(hdf5_file["boards"].values())[0].values())[0].values()
        )[0].keys()
        if read_session != "bitstreams"
    ]
    hdf5_file.create_dataset(
        "read_session_names", (len(read_session_names),), data=read_session_names
    )


parser = argparse.ArgumentParser(
    "Script converts read bram data structured in directories, to hdf5"
)
parser.add_argument(
    "-r", "--root_dir", help="Base directory of read data", required=True
)

if __name__ == "__main__":
    args = parser.parse_args()
    date = str(datetime.datetime.now())
    arg_dict = vars(args)
    root_path = Path(arg_dict["root_dir"])
    print(f"{root_path}_{date}.hdf5")
    with h5py.File(f"{root_path}_{date}.hdf5", "w") as f:
        root_group = f

        add_meta_data_from_json(root_group, Path(root_path, "meta_data.json"))
        add_boards_group(Path(root_path, "boards"), root_group)
        derivate_read_session_names(f)
