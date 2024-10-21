"""
Contains infrastructure (Boilerplate classes) that makes managing hdf5 experiment files easier
"""

import numpy as np
import h5py
from dataclasses import dataclass, field
from typing import List, Dict, Self
from scipy.stats import entropy
from functools import cached_property, reduce

@dataclass
class Read:
    raw_read: bytes
    bits: np.ndarray = field(init=False)

    def __post_init__(self):
        uint8_read = np.frombuffer(self.raw_read, dtype=np.uint8)
        self.bits = np.unpackbits(uint8_read).reshape(len(self.raw_read), 8)

    @cached_property
    def bits_flatted(self) -> np.ndarray:
        return self.bits.flatten()
    
    @cached_property
    def entropy(self) -> float:
        return entropy(self.bits_flatted, base=2)

@dataclass
class ReadSession:
    data_reads: List[Read]
    parity_reads: List[Read]
    temperatures: List[float]

    @classmethod
    def from_hdf5(cls, hdf5_group: h5py.Group) -> "ReadSession":
        data_read_dataset = hdf5_group["data_reads"]
        data_reads = [Read(bytes(read)) for read in data_read_dataset]

        parity_read_dataset = hdf5_group["parity_reads"]
        parity_reads = [Read(bytes(read)) for read in parity_read_dataset]

        temperatures = [temperature for temperature in hdf5_group["temperature"]]

        return cls(data_reads, parity_reads, temperatures)
    
    def __add__(self, other: Self) -> Self:
        return ReadSession(
            self.data_reads + other.data_reads,
            self.parity_reads + other.parity_reads,
            self.temperatures + other.temperatures
        )
    


@dataclass
class BramBlock:
    # Currently not used because it is not needed and only wastes ram
    # bitstreams: bytes
    name: str
    read_sessions: Dict[str, ReadSession]

    @classmethod
    def from_hdf5(cls, hdf5_group: h5py.Group, name: str) -> "BramBlock":
        read_sessions = {
            key: ReadSession.from_hdf5(hdf5_group[key])
            for key in hdf5_group
            # Skip bs directory
            if key != "bitstreams"
        }

        return cls(name, read_sessions)

@dataclass
class PBlock:
    name: str
    bram_blocks: Dict[str, BramBlock]

    @classmethod
    def from_hdf5(cls, hdf5_group: h5py.Group, name: str) -> "PBlock":
        bram_blocks = {
            key: BramBlock.from_hdf5(hdf5_group[key], key)
            for key in hdf5_group
            if "RAMB36" in key
        }
        return cls(name, bram_blocks)
    
    def flatten(self) -> Dict[str, ReadSession]:
        "Merges read sessions of all brams for each keyword"
        return {
            read_session_key: reduce(lambda x, y: x+y, [
                bram_block.read_sessions[read_session_key]
                for bram_block in self.bram_blocks.values()
            ])
            for read_session_key in self.bram_blocks.values()[0].read_sessions
        }

@dataclass
class Board:
    board_name: str
    fpga: str
    uart_sn: str
    programming_interface: str
    date: str
    pblocks: Dict[str, PBlock]

    @classmethod
    def from_hdf5(cls, hdf5_group: h5py.Group) -> "Board":
        kw_args = {
            attr_name: hdf5_group.attrs[attr_name]
            for attr_name in ["board_name", "fpga", "uart_sn", "programming_interface", "date"]
        }

        pblocks = {
            key: PBlock.from_hdf5(hdf5_group[key], key) 
            for key in hdf5_group 
            if "pblock" in key
        }
        kw_args["pblocks"] = pblocks

        return cls(**kw_args)
    
    def flatten(self) -> Dict[str, ReadSession]:
        "Merges read sessions of all brams of all pblocks for each keyword"
        return {
            read_session_key: reduce(lambda x, y: x+y, [
                pblock.flatte()
                for pblock in self.pblocks.values()
            ])
            for read_session_key in self.pblocks.values()[0].flatten()
        }

@dataclass
class Experiment:
    boards: Dict[str, Board]
    commit: str
    read_session_names: list[str]

    @classmethod
    def from_hdf5(cls, hdf5_group: h5py.Group, commit: str) -> "Experiment":
        boards = {
            board: Board.from_hdf5(hdf5_group["boards"][board]) 
            for board in hdf5_group["boards"]
        }
        read_session_names = [binary_str.decode() for binary_str in hdf5_group["read_session_names"]]

        return cls(boards, commit, read_session_names)
