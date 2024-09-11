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


def add_bram_read_dataset(path: Path, parent: h5py._hl.group.Group, name: str, binary: bool = False) -> None:
    '''
    Adds bram reads as a dataset to <bram_name>/<0-to-f or f-to-0> group

    Parameters:
        path: Path to directory that contains multiple bram reads
        parent: Parent group of dataset
        name: Name of the dataset (should be either "data" or "parity")
        binary: Is read saved in binary or ASCII?
    '''
    
    # Sort files numerically ascending: [0, 1, 2, ..., 10, ...]
    # This is done to avoid: [0, 1, 10, 100, 1000, 2, 20,...] 
    files_sorted_by_index = sorted(
        [
            file_path for file_path in path.iterdir()
            if file_path.is_file()
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

    parent.create_dataset(name, read_data, dtype=h5py.string_dtype(length=seq_length))



def add_bram_group(path: Path, parent: h5py._hl.group.Group) -> None:
    '''
    Adds measurement Data from single BRAM experiment as path to a given parent group

    Parameters:
        path: Path to BRAM measurements in (Linux)filesystem
        parent: Parent group of new group
    '''

    bram_name = path.parts[-1]

    parent.create_group(bram_name)

    # Create temperature dataset
    temperature_path = Path(path, "temperature.txt") 
    if temperature_path.exists() and temperature_path.is_file():
        pass

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

if __name__ == "__main__":
    args = parser.parse_args()
    date = str(datetime.datetime())
    with open(f"{args["root_dir"]}_{date}.hdf5", "w") as f:
        root_group = f.create_group("base")

        meta_data = vars(args)
        meta_data.pop("root_dir")

        add_meta_data(root_group, meta_data)

        