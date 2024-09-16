import h5py
from pathlib import Path
from typing import Dict
import datetime
import argparse

# General:
# Sometimes experiments may fail and/or are interrupted
# This could lead to an incomplete file structure
# We therefore do not assume that all subconstituents of 
#   a BRAM experiment are always available

def add_meta_data(parent: h5py._hl.group.Group, meta_data: Dict[str, str]) -> None:
    '''
    Adds relevant meta data to hdf5 groupe
    '''
    for key, value in meta_data.items():
        parent.attrs[key] = value


def add_temperature_dataset(temperature_file: Path, parent: h5py._hl.group.Group) -> None:
    '''
    Adds temperature data set to <bram_name>/<0-to-f or f-to-0> group

    Parameters:
        temperature_file: Path to temperature.txt file
        parent: Parent group of dataset
    '''

    with open(temperature_file, mode="r") as f:
        # Zynq FPGAs will have two temperature sensors (PL and PS)
        # We assume the first output to be the temperature of PL
        values = [
            float(measurement.split()[0].strip()) 
            for measurement in f.readlines()
        ]

        parent.create_dataset("temperature" ,values, dtype=f)


def add_bram_dataset_group(path: Path, parent: h5py._hl.group.Group, group_name: str, binary: bool = False) -> None:
    '''
    Adds bram reads as a dataset to <bram_name>/<0-to-f or f-to-0> group

    Parameters:
        path: Path to directory that contains multiple bram reads
        parent: Parent group of dataset
        name: Name of the dataset (should be either "data" or "parity")
        binary: Is read saved in binary or ASCII?
    '''
    bram_data_group = parent.create_group(group_name)

    # Sort files numerically ascending: [0, 1, 2, ..., 10, ...]
    # This is done to avoid: [0, 1, 10, 100, 1000, 2, 20,...] 
    files_sorted_by_index = sorted(
        [
            file_path for file_path in path.iterdir()
            if file_path.is_file() and file_path.name != "temperature.txt"
        ],
        key=lambda x: int(x.stem)
    )

    read_data = []
    for file in files_sorted_by_index:
        with open(file, mode=("rb" if binary else "r")) as f:
            read_data.append(f.read())
    seq_length =  len(read_data[0])
    
    # Quality control
    assert all([len(read) == seq_length for read in read_data])

    bram_data_group.create_dataset("measurements", read_data, dtype=h5py.string_dtype(length=seq_length))

    # Add temperature if available
    temperature_path = Path(path, "temperature.txt") 
    if temperature_path.exists() and temperature_path.is_file():
        add_temperature_dataset(Path(path, "temperature.txt"), bram_data_group)


def add_bitstream_group(path: Path, parent: h5py._hl.group.Group) -> None:

    bs_files = [
        file_path for file_path in path.iterdir()
        if file_path.is_file()
    ]

    bitstream_group = parent.create_group("bitstreams")

    # Add five bitstreams as attributes
    for bs in bs_files:
        match bs.stem.split("_"):
            case [*_, "partial", "bram", "bs"]:
                with open(bs, mode="rb") as f:
                    bitstream_group.attrs["partial_bram_bs"] = f.read()
            case [*_, "modified", "partial"]:
                with open(bs, mode="rb") as f:
                    bitstream_group.attrs["modified_partial"] = f.read()
            case [*_, "ff"]:
                with open(bs, mode="rb") as f:
                    bitstream_group.attrs["ff"] = f.read()
            case [*_, "00"]:
                with open(bs, mode="rb") as f:
                    bitstream_group.attrs["00"] = f.read()
            case [*_, "bramless", "partial"]:
                with open(bs, mode="rb") as f:
                    bitstream_group.attrs["bramless_partial"] = f.read()
    

def add_bram_group(path: Path, parent: h5py._hl.group.Group, binary: bool = False) -> None:
    '''
    Adds measurement Data from single BRAM experiment as path to a given parent group
    - Adds measurements with previous value ff and 00 if available)
    - Also adds bitstreams if available

    Parameters:
        path: Path to BRAM measurements in (Linux)filesystem
        parent: Parent group of new group
        binary: True if measurements were done in binary
    '''

    bram_name = path.parts[-1]

    bram_group = parent.create_group(bram_name)

    expected_paths = [
        Path(path, "previous_value_ff"),
        Path(path, "previous_value_00")
    ]
    
    for expected_path in expected_paths:
        if expected_path.exists() and expected_path.is_dir():
            add_bram_dataset_group(expected_path, bram_group, expected_path.parts[-1], binary)
    
    bs_path = Path(path, "bs")
    if bs_path.exists() and bs_path.is_dir():
        add_bitstream_group(bs_path, bram_group)

def add_pblock_group(path: Path, parent: h5py._hl.group.Group, binary: bool = False) -> None:
    '''
    Adds all bram data directories from a given pblock directory
    '''

    pblock_name = path.parts[-1]
    pblock_group = parent.create_group(pblock_name)

    bram_dirs = [
        sub_path for sub_path in path.iterdir()
        if sub_path.is_dir() and "RAMB" in sub_path.parts[-1]
    ]

    for bram_dir in bram_dirs:
        add_bram_group(bram_dir, pblock_group, binary)

parser = argparse.ArgumentParser("Script converts read bram data structured in directories, to hdf5")
parser.add_argument(
    "-r", "--root_dir",
    help="Base directory of read data"
)
parser.add_argument(
    "-f", "--fpga",
    help="Name of fpga used for experiment"
)
parser.add_argument(
    "-c", "--commit",
    help="Latest commit used for experiment"
)
parser.add_argument(
    "-j", "--jtag_sn",
    help="Serial number of jtag interface that was used to flash fpga"
)
parser.add_argument(
    "-u", "--uart_sn",
    help="Serial number of uart adapter that was used to read bram"
)
parser.add_argument(
    "-b", "--binary_files",
    help="Read data was saved in binary files.",
    action="store_true"
)

if __name__ == "__main__":
    args = parser.parse_args()
    date = str(datetime.datetime())
    with open(f"{args["root_dir"]}_{date}.hdf5", "w") as f:
        root_group = f.create_group("base")
        
        meta_data = vars(args)
        root_path = Path(meta_data["root_dir"])
        use_binary_files = meta_data["binary_fils"]
        meta_data.pop("root_dir")
        meta_data.pop("binary_files")

        add_meta_data(root_group, meta_data)

        # Iterate through all pblocks in given base directory
        pblock_dirs = [
            sub_path for sub_path in root_path.iterdir()
            if sub_path.is_dir() and "pblock" in sub_path.parts[-1]
        ]

        for pblock_dir in pblock_dirs:
            add_pblock_group(pblock_dir, root_group, use_binary_files)
        