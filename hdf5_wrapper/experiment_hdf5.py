"""
Contains infrastructure (Boilerplate classes) that makes managing hdf5 experiment files easier
"""

import numpy as np
import numpy.typing as npt
import h5py
from abc import ABC
from dataclasses import dataclass, field
from typing import List, Dict, Self
from scipy.stats import entropy
from functools import cached_property, reduce

@dataclass(frozen=True)
class Read:
    raw_read: bytes
    bits: npt.NDArray

    @cached_property
    def bits_flattened(self) -> npt.NDArray[np.float64]:
        return self.bits.flatten()
    
    @cached_property
    def entropy(self) -> np.float64:
        value, counts = np.unique(self.bits_flattened, return_counts=True)
        return entropy(counts, base=2)
    
    @classmethod
    def from_raw(cls, raw_read: bytes):
        uint8_read = np.frombuffer(raw_read, dtype=np.uint8)
        bits = np.unpackbits(uint8_read).reshape(len(raw_read), 8)
        return cls(raw_read, bits)
    
    

@dataclass(frozen=True)
class ReadSession:
    data_reads: List[Read]
    parity_reads: List[Read]
    temperatures: List[float]

    @classmethod
    def from_hdf5(cls, hdf5_group: h5py.Group) -> "ReadSession":
        data_read_dataset = hdf5_group["data_reads"]
        data_reads = [Read.from_raw(bytes(read)) for read in data_read_dataset]

        parity_read_dataset = hdf5_group["parity_reads"]
        parity_reads = [Read.from_raw(bytes(read)) for read in parity_read_dataset]

        temperatures = [temperature for temperature in hdf5_group["temperature"]]

        return cls(data_reads, parity_reads, temperatures)
    
    def __add__(self, other: Self) -> Self:
        return ReadSession(
            self.data_reads + other.data_reads,
            self.parity_reads + other.parity_reads,
            self.temperatures + other.temperatures
        )
    
    @classmethod
    def merge_from_list(cls, read_sessions: list[Self]) -> Self:
        """
        More efficient version of __add__ if multiple read sessions are added at once
        """
        merged_data_reads = list()
        merged_parity_reads = list()
        merged_temperatures = list()

        for read_session in read_sessions:
            merged_data_reads += read_session.data_reads
            merged_parity_reads += read_session.parity_reads
            merged_temperatures += read_session.temperatures

        return cls(merged_data_reads, merged_parity_reads, merged_temperatures)

@dataclass(frozen=True, kw_only=True)
class ExperimentContainer(ABC):
    name: str
    subcontainers: dict[str, Self]
    read_session_names: list[str]
    read_sessions: dict[str, ReadSession] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Merge all ReadSession from Subcontainers in own ReadSession
        sample_subcontainer = list(self.subcontainers.values())[0]
        for read_session_name in sample_subcontainer.read_sessions:
            self.read_sessions[read_session_name] = ReadSession.merge_from_list(
                [
                    container.read_sessions[read_session_name]
                    for container in self.subcontainers.values()
                ]
            )

@dataclass(frozen=True, kw_only=True)
class BramBlock:
    # Currently not used because it is not needed and only wastes ram
    # bitstreams: bytes
    name: str
    read_sessions: Dict[str, ReadSession]
    read_session_names: list[str]

    @classmethod
    def from_hdf5(cls, hdf5_group: h5py.Group, name: str, read_session_names: list[str]) -> "BramBlock":
        read_sessions = {
            key: ReadSession.from_hdf5(hdf5_group[key])
            for key in hdf5_group
            # Skip bs directory
            if key != "bitstreams"
        }

        return cls(name=name, read_sessions=read_sessions, read_session_names=read_session_names)


@dataclass(frozen=True, kw_only=True)
class PBlock(ExperimentContainer):
    subcontainers: Dict[str, BramBlock]


    @classmethod
    def from_hdf5(cls, hdf5_group: h5py.Group, name: str, read_session_names: list[str]) -> "PBlock":
        bram_blocks = {
            key: BramBlock.from_hdf5(hdf5_group[key], key, read_session_names=read_session_names)
            for key in hdf5_group
            if "RAMB36" in key
        }
        return cls(name=name, subcontainers=bram_blocks, read_session_names=read_session_names)
    
    def flatten(self) -> Dict[str, ReadSession]:
        "Merges read sessions of all brams for each keyword"
        return {
            read_session_key: reduce(lambda x, y: x+y, [
                bram_block.read_sessions[read_session_key]
                for bram_block in self.subcontainers.values()
            ])
            for read_session_key in self.subcontainers.values()[0].read_sessions
        }

@dataclass(frozen=True, kw_only=True)
class Board(ExperimentContainer):
    fpga: str
    uart_sn: str
    programming_interface: str
    date: str
    subcontainers: Dict[str, PBlock]
    read_session_names: list[str]

    @classmethod
    def from_hdf5(cls, hdf5_group: h5py.Group, read_session_names: list[str]) -> "Board":
        kw_args = {
            attr_name: hdf5_group.attrs[attr_name]
            for attr_name in ["board_name", "fpga", "uart_sn", "programming_interface", "date"]
        }

        # This is a fix because attribute is named "board_name" instead of name in experiment hdf5
        kw_args["name"] = kw_args["board_name"]
        kw_args.pop("board_name")

        pblocks = {
            key: PBlock.from_hdf5(hdf5_group[key], key, read_session_names=read_session_names) 
            for key in hdf5_group 
            if "pblock" in key
        }
        kw_args["subcontainers"] = pblocks
        kw_args["read_session_names"] = read_session_names

        return cls(**kw_args)
    
    def flatten(self) -> Dict[str, ReadSession]:
        "Merges read sessions of all brams of all pblocks for each keyword"
        return {
            read_session_key: reduce(lambda x, y: x+y, [
                pblock.flatte()
                for pblock in self.subcontainers.values()
            ])
            for read_session_key in self.subcontainers.values()[0].flatten()
        }

@dataclass(frozen=True)
class Experiment(ExperimentContainer):
    subcontainers: Dict[str, Board]
    commit: str
    read_session_names: list[str]

    @classmethod
    def from_hdf5(cls, hdf5_group: h5py.Group, commit: str) -> "Experiment":
        read_session_names = [binary_str.decode() for binary_str in hdf5_group["read_session_names"]]

        boards = {
            board: Board.from_hdf5(hdf5_group["boards"][board], read_session_names=read_session_names) 
            for board in hdf5_group["boards"]
        }

        return cls(name="experiment", subcontainers=boards, commit=commit, read_session_names=read_session_names)
