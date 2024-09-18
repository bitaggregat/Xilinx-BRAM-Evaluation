"""
Contains infrastructure (Boilerplate classes) that makes managing hdf5 experiment files easier
"""

import numpy as np
import h5py
from dataclasses import dataclass, field
from typing import List, Dict


class Read(dataclass):
    raw_read: bytes
    bits: np.array = field(init=False)

    def __post_init__(self):
        uint8_read = np.frombuffer(self.raw_read, dtype=np.uint8)
        self.bits = np.unpackbits(uint8_read).reshape(len(self.raw_read), 8)


class ReadSession(dataclass):
    data_reads: List[Read]
    parity_reads: List[Read]
    temperatures: List[float]

    @classmethod
    def from_hdf5(cls, hdf5_group: h5py._hl.group.Group) -> "ReadSession":
        data_read_dataset = hdf5_group["data_reads"]
        data_reads = [Read(read) for read in data_read_dataset]

        parity_read_dataset = hdf5_group["parity_reads"]
        parity_reads = [Read(read) for read in parity_read_dataset]

        temperatures = [temperature for temperature in hdf5_group["temperature"]]

        return cls(data_reads, parity_reads, temperatures)


class BramBlock(dataclass):
    # Currently not used because it is not needed and only wastes ram
    # bitstreams: bytes
    name: str
    read_sessions: Dict[str, ReadSession]

    @classmethod
    def from_hdf5(cls, hdf5_group: h5py._hl.group.Group) -> "BramBlock":
        read_sessions = {
            key: ReadSession.from_hdf5(hdf5_group[key])
            for key in hdf5_group
            # Skip bs directory
            if key != "bs"
        }
        name = hdf5_group.attrs["name"]

        return cls(name, read_sessions)


class PBlock(dataclass):
    name: str
    bram_blocks: Dict[str, BramBlock]

    @classmethod
    def from_hdf5(cls, hdf5_group: h5py._hl.group.Group) -> "PBlock":
        bram_blocks = {
            key: BramBlock.from_hdf5(hdf5_group[key])
            for key in hdf5_group
            if "RAMB36" in key
        }
        name = hdf5_group.attrs["name"]
        return cls(name, bram_blocks)


class Board(dataclass):
    name: str
    fpga: str
    uart_adapter_sn: str
    jtag_sn: str
    date: str
    pblocks: Dict[str, PBlock]

    @classmethod
    def from_hdf5(cls, hdf5_group: h5py._hl.group.Group) -> "Board":
        kw_args = {
            attr_name: hdf5_group.attrs[attr_name]
            for attr_name in ["name", "fpga", "uart_adapter_sn", "jtag_sn", "date"]
        }

        pblocks = {
            key: PBlock.from_hdf5(hdf5_group[key]) 
            for key in hdf5_group 
            if "pblock" in key
        }
        kw_args["pblocks"] = pblocks

        return cls(**kw_args)


class Experiment(dataclass):
    boards: Dict[str, Board]
    commit: str

    @classmethod
    def from_hdf5(cls, hdf5_group: h5py._hl.group.Group, commit: str) -> "Experiment":
        boards = {
            board: Board.from_hdf5(board) 
            for board in hdf5_group["boards"]
        }

        return cls(boards, commit)
