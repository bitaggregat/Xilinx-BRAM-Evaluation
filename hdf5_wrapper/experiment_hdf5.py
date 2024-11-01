"""
Contains infrastructure (Boilerplate classes) that makes managing hdf5 experiment files easier.
Structures measurement data into objects that represent entities from the experiment.
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
    """
    Wrapper around a single read value of the BRAM
    - also sometimes called SUV (start up value)
    """

    raw_read: bytes
    # Has shape (x, 8)
    # Not noted in type hint because numpy type hinting best practice is currently going through changes
    bits: npt.NDArray

    @cached_property
    def bits_flattened(self) -> npt.NDArray[np.float64]:
        return self.bits.flatten()

    @cached_property
    def entropy(self) -> np.float64:
        """
        Counts 1's and 0's in read value. Then computes entropy over those counts
        """
        value, counts = np.unique(self.bits_flattened, return_counts=True)
        return entropy(counts, base=2)

    @classmethod
    def from_raw(cls, raw_read: bytes) -> Self:
        uint8_read = np.frombuffer(raw_read, dtype=np.uint8)
        bits = np.unpackbits(uint8_read).reshape(len(raw_read), 8)
        return cls(raw_read, bits)


@dataclass(frozen=True)
class ReadSession:
    """
    Container that gathers lists of reads of same the read session.
    A read session is defined as a context under which the reads were measured.
    - e.g.:
        - there can be a ReadSession for Temperature T:=ambient
        - and there can be a different ReadSession for T:=60°
    - data and parity reads are related because they are measured at the same time
        - e.g. data_reads[0] was taken at the same time as parity_reads[0]
    """

    # ReadSession's (and many other objects)
    # differentiate between data and parity reads.
    # Both are SRAM bits that can be written and read from the BRAM.
    # We separated them because we assume(d) that they may behave differently.
    data_reads: List[Read]
    parity_reads: List[Read]
    temperatures: List[float]

    @classmethod
    def from_hdf5(cls, hdf5_group: h5py.Group) -> "ReadSession":
        """
        Parses this object from a hdf5 subgroup, belonging to a experiment hdf5 file
        """
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
            self.temperatures + other.temperatures,
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
class BramBlock:
    """
    Container that gathers all ReadSession's of the same bram block
    """

    name: str  # name of bram block: e.g. RAMB36_X2Y12
    read_sessions: Dict[str, ReadSession]
    read_session_names: list[str]

    @classmethod
    def from_hdf5(
        cls, hdf5_group: h5py.Group, name: str, read_session_names: list[str]
    ) -> Self:
        """
        Parses this object from a hdf5 subgroup, belonging to a experiment hdf5 file
        """
        read_sessions = {
            key: ReadSession.from_hdf5(hdf5_group[key])
            for key in hdf5_group
            # Skip bs directory of experiment hdf5 file
            if key != "bitstreams"
        }

        return cls(
            name=name,
            read_sessions=read_sessions,
            read_session_names=read_session_names,
        )


@dataclass(frozen=True, kw_only=True)
class ExperimentContainer(ABC):
    """
    Generalization of containers that represent different layer entities of an experiment.
    e.g.:
        - Container for all bram blocks in a pblock
        - or all pblocks on a device
    Reduces code duplicates
    Note: BramBlock is not included because it does not own other "subcontainers"
    """

    name: str
    subcontainers: dict[str, Self | BramBlock]
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
class PBlock(ExperimentContainer):
    """
    See ExperimentContainer
    """

    subcontainers: Dict[str, BramBlock]

    @classmethod
    def from_hdf5(
        cls, hdf5_group: h5py.Group, name: str, read_session_names: list[str]
    ) -> Self:
        """
        Parses this object from a hdf5 subgroup, belonging to a experiment hdf5 file
        """
        bram_blocks = {
            key: BramBlock.from_hdf5(
                hdf5_group[key], key, read_session_names=read_session_names
            )
            for key in hdf5_group
            if "RAMB36" in key
        }
        return cls(
            name=name, subcontainers=bram_blocks, read_session_names=read_session_names
        )

    def flatten(self) -> Dict[str, ReadSession]:
        """
        Merges read sessions of all brams for each keyword
        """
        return {
            read_session_key: reduce(
                # adds all lists into a single one
                lambda x, y: x + y,
                [
                    bram_block.read_sessions[read_session_key]
                    for bram_block in self.subcontainers.values()
                ],
            )
            for read_session_key in self.subcontainers.values()[0].read_sessions
        }


@dataclass(frozen=True, kw_only=True)
class Board(ExperimentContainer):
    """
    See ExperimentContainer
    """

    fpga: str
    uart_sn: str
    programming_interface: str
    date: str
    subcontainers: Dict[str, PBlock]

    @classmethod
    def from_hdf5(cls, hdf5_group: h5py.Group, read_session_names: list[str]) -> Self:
        """
        Parses this object from a hdf5 subgroup, belonging to a experiment hdf5 file
        """

        # Reducing code mass by using kwargs
        kwargs = {
            attr_name: hdf5_group.attrs[attr_name]
            for attr_name in [
                "board_name",
                "fpga",
                "uart_sn",
                "programming_interface",
                "date",
            ]
        }

        # This is a fix because attribute is named "board_name" instead of name in experiment hdf5
        kwargs["name"] = kwargs["board_name"]
        kwargs.pop("board_name")

        pblocks = {
            key: PBlock.from_hdf5(
                hdf5_group[key], key, read_session_names=read_session_names
            )
            for key in hdf5_group
            if "pblock" in key
        }
        kwargs["subcontainers"] = pblocks
        kwargs["read_session_names"] = read_session_names

        return cls(**kwargs)

    def flatten(self) -> Dict[str, ReadSession]:
        """
        Merges read sessions of all brams of all pblocks for each keyword
        """
        return {
            read_session_key: reduce(
                lambda x, y: x + y,
                [pblock.flatten() for pblock in self.subcontainers.values()],
            )
            for read_session_key in self.subcontainers.values()[0].flatten()
        }


@dataclass(frozen=True)
class Experiment(ExperimentContainer):
    """
    See ExperimentContainer
    - Highest layer of ExperimentContainers
    """

    subcontainers: Dict[str, Board]
    commit: str

    @classmethod
    def from_hdf5(cls, hdf5_group: h5py.Group, commit: str) -> Self:
        """
        Parses this object from a hdf5 subgroup, belonging to a experiment hdf5 file
        """
        read_session_names = [
            binary_str.decode() for binary_str in hdf5_group["read_session_names"]
        ]

        boards = {
            board: Board.from_hdf5(
                hdf5_group["boards"][board], read_session_names=read_session_names
            )
            for board in hdf5_group["boards"]
        }

        return cls(
            name="experiment",
            subcontainers=boards,
            commit=commit,
            read_session_names=read_session_names,
        )
