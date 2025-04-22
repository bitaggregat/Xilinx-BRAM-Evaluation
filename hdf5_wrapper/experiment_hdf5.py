"""
Contains infrastructure (Boilerplate classes) that
makes managing hdf5 experiment files easier.
Structures measurement data into objects that
represent entities from the experiment.
"""

import numpy as np
import numpy.typing as npt
import h5py
from abc import ABC
from dataclasses import dataclass, field
from typing import List, Dict, Self
from scipy.stats import entropy
from functools import cached_property, reduce
from scipy.spatial.distance import hamming


@dataclass(frozen=True)
class Read:
    """
    Wrapper around a single read value of the BRAM
    - also sometimes called SUV (start up value)

    Attributes:
        raw_read: SUV as bytes object
        bits: SUV as numpy array. Has shape (x, 8)
    """

    raw_read: bytes | None
    # Not noted in type hint because numpy type hinting best practice
    bits: npt.NDArray[np.int8]

    @property
    def bits_flattened(self) -> npt.NDArray[np.float64]:
        return self.bits.flatten()

    @property
    def bits_flattened_bool(self) -> npt.NDArray[np.bool_]:
        return np.array(self.bits_flattened, dtype=bool)

    @property
    def entropy(self) -> np.float64:
        """
        Counts 1's and 0's in read value.
        Then computes entropy over those counts
        """
        value, counts = np.unique(self.bits_flattened, return_counts=True)
        return entropy(counts, base=2)

    @classmethod
    def from_raw(
        cls, raw_read: bytes, remove_signature_bits: bool = False, 
        cache_raw_read: bool = False
    ) -> Self:
        """
        Creates Read object from raw read.
        Args:
            raw_read (bytes): Single read of bram startup value
        """
        uint8_read = np.frombuffer(raw_read, dtype=np.uint8)
        bits = np.unpackbits(uint8_read).reshape(len(raw_read), 8)
        if remove_signature_bits:
            bits = np.concatenate([bits[32:32*64], bits[33*64:-32]], axis=0)
        if cache_raw_read:
            return cls(raw_read, bits)
        else:
            return cls(None, bits)

    def filter_stripe(self, filter_even_stripes: bool) -> Self:
        new_bit_parts = []
        sub_array_count = (len(self.bits)-8)/8
        if filter_even_stripes:
            new_bit_parts.append(self.bits[0:4])
            temp_sub_arrays = np.array(np.split(self.bits[4:-4], sub_array_count))
            new_bit_parts += [subarray for subarray in (temp_sub_arrays[1::2])]
            new_bit_parts.append(self.bits[-4:])
            new_bits = np.concatenate(new_bit_parts, axis=0)
        else:
            temp_sub_arrays = np.array(np.split(self.bits[4:-4], sub_array_count))
            new_bits = np.array([subarray for subarray in (temp_sub_arrays[::2])])
        return Read(b"", new_bits)


def reliability_with_predefined_value(
    comparison_value: Read, reads: list[Read]
) -> np.float64:
    """ """
    r_i = comparison_value.bits_flattened
    intradistance_sum = sum(
        [hamming(r_i, other_read.bits_flattened) for other_read in reads]
    )
    normalized_avg_intradistance = intradistance_sum / len(reads)
    return (1 - normalized_avg_intradistance) * 100


@dataclass(frozen=True)
class ReadSession:
    """
    Container that gathers lists of reads of same the read session.
    A read session is defined as a context under which the reads were measured.
    - e.g.:
        - there can be a ReadSession for Temperature T:=ambient
        - and there can be a different ReadSession for T:=60°
    - data and parity reads are related because
      they are measured at the same time
        - e.g. data_reads[0] was taken at the same time as parity_reads[0]

    Attributes:
        data_reads: Read's made from brams "regular" bits' startup values
        parity_reads: Read's made from brams parity bits' startup values
        temperatures: Temperature values after each readout procedure
                      (Index parallel to data_ and parity_reads)
    """

    # ReadSession's (and many other objects)
    # differentiate between data and parity reads.
    # Both are SRAM bits that can be written and read from the BRAM.
    # We separated them because we assume(d) that they may behave differently.
    data_reads: List[Read]
    parity_reads: List[Read]
    temperatures: List[float]

    @classmethod
    def from_hdf5(
        cls,
        hdf5_group: h5py.Group,
        filter_even_stripes: bool = False,
        filter_uneven_stripes: bool = False,
        cache_raw_reads: bool = False
    ) -> "ReadSession":
        """
        Parses this object from a hdf5 subgroup,
        belonging to a experiment hdf5 file
        """
        data_read_dataset = hdf5_group["data_reads"]
        if filter_even_stripes or filter_uneven_stripes:
            data_reads = [Read.from_raw(bytes(read), remove_signature_bits=True, cache_raw_read=cache_raw_reads) for read in data_read_dataset]
        else:
            data_reads = [Read.from_raw(bytes(read), cache_raw_read=cache_raw_reads) for read in data_read_dataset]
        if filter_even_stripes:
            data_reads = [
                read.filter_stripe(filter_even_stripes=True)
                for read in data_reads
            ]
        if filter_uneven_stripes:
            data_reads = [
                read.filter_stripe(filter_even_stripes=False)
                for read in data_reads
            ]

        parity_read_dataset = hdf5_group["parity_reads"]
        parity_reads = [
            Read.from_raw(bytes(read), cache_raw_read=cache_raw_reads) for read in parity_read_dataset
        ]

        temperatures = [
            temperature for temperature in hdf5_group["temperature"]
        ]

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
        More efficient version of __add__ if multiple read sessions
        are added at once

        Args:
            read_sessions: List of ReadSession's objects that shall be merged
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

    Attributes:
        name: Name of bram block: e.g. RAMB36_X2Y12
        read_sessions: ReadSession objects mapped by their name
        read_session_names: Names of all existings ReadSession's
    """

    name: str
    read_sessions: Dict[str, ReadSession]
    read_session_names: list[str]
    bram_count: int = field(init=False, default=1)

    @property
    def read_sessions_unmerged(self) -> dict[str, list[ReadSession]]:
        return {
            read_session_name: [self.read_sessions[read_session_name]]
            for read_session_name in self.read_session_names
        }

    def reliability_intercomparison(
        self, base_session_name: str
    ) -> dict[str, np.float64]:
        comparison_element = self.read_sessions[base_session_name].data_reads[
            0
        ]
        reliability_per_session_dict = dict()
        for read_session in self.read_session_names:
            reads = self.read_sessions[read_session].data_reads
            if read_session == base_session_name:
                reads = reads[1:]
            reliability_per_session_dict[read_session] = (
                reliability_with_predefined_value(comparison_element, reads)
            )
        return reliability_per_session_dict

    @classmethod
    def from_hdf5(
        cls,
        hdf5_group: h5py.Group,
        name: str,
        read_session_names: list[str],
        filter_even_stripes: bool = False,
        filter_uneven_stripes: bool = False,
    ) -> Self:
        """
        Parses this object from a hdf5 subgroup,
        belonging to a experiment hdf5 file
        """
        read_sessions = {
            key: ReadSession.from_hdf5(
                hdf5_group[key],
                filter_even_stripes=filter_even_stripes,
                filter_uneven_stripes=filter_uneven_stripes,
            )
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
    Generalization of containers that represent different layer entities
    of an experiment.
    e.g.:
        - Container for all bram blocks in a pblock
        - or all pblocks on a device
    Reduces code duplicates
    Note: BramBlock is not included because
          it does not own other "subcontainers"

    Attributes:
        name: Name of experiment container (e.g. pblock_x or "device_y")
        subcontainers: Subordinated containers (e.g. a device has multiple
                        pblocks and a pblock has multiple bram blocks)
        read_sessions: ReadSession objects mapped by their name
        read_session_names: Names of all existings ReadSession's
    """

    name: str
    bram_count: int
    subcontainers: dict[str, Self | BramBlock]
    read_session_names: list[str]
    read_sessions: dict[str, ReadSession] = field(default_factory=dict)
    read_sessions_unmerged: dict[str, list[ReadSession]] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        # Merge all ReadSession from Subcontainers in own ReadSession
        sample_subcontainer = list(self.subcontainers.values())[0]
        for read_session_name in sample_subcontainer.read_sessions:
            self.read_sessions[read_session_name] = (
                ReadSession.merge_from_list(
                    [
                        container.read_sessions[read_session_name]
                        for container in self.subcontainers.values()
                    ]
                )
            )

            self.read_sessions_unmerged[read_session_name] = [
                read_session
                for container in self.subcontainers.values()
                for read_session in container.read_sessions_unmerged[
                    read_session_name
                ]
            ]
            pass


@dataclass(frozen=True, kw_only=True)
class PBlock(ExperimentContainer):
    """
    See ExperimentContainer
    """

    subcontainers: Dict[str, BramBlock]

    def reliability_intercomparison(
        self, base_session_name: str
    ) -> tuple[dict[str, list[np.float64]], list[str]]:
        bram_names = list()
        session_values = {
            session_name: list() for session_name in self.read_session_names
        }
        print(session_values)
        for bram in self.subcontainers.values():
            bram_names.append(bram.name)
            temp_reliability_values = bram.reliability_intercomparison(
                base_session_name
            )
            for read_session, value in temp_reliability_values.items():
                session_values[read_session].append(value)
        print(session_values)
        return session_values, bram_names

    @classmethod
    def from_hdf5(
        cls, hdf5_group: h5py.Group, name: str, read_session_names: list[str],
        filter_even_stripes: bool = False,
        filter_uneven_stripes: bool = False
    ) -> Self:
        """
        Parses this object from a hdf5 subgroup, belonging
        to a experiment hdf5 file
        """
        bram_blocks = {
            key: BramBlock.from_hdf5(
                hdf5_group[key], key, read_session_names=read_session_names,
                filter_even_stripes=filter_even_stripes,
                filter_uneven_stripes=filter_uneven_stripes
            )
            for key in hdf5_group
            if "RAMB36" in key
        }
        bram_count = sum([bram.bram_count for bram in bram_blocks.values()])
        return cls(
            name=name,
            bram_count=bram_count,
            subcontainers=bram_blocks,
            read_session_names=read_session_names,
        )


@dataclass(frozen=True, kw_only=True)
class Board(ExperimentContainer):
    """
    See ExperimentContainer

    Attributes:
        fpga: Name of fpga. Not to be confused with device name (e.g.
                device:=te0802 but fpga:=zu1eg
        uart_sn: Serial number of UART device used for measurements
        programming_interface: Serial number of jtag programming interface
        data: Date of measurement of board
        subcontainers: See ExperimentContainer
    """

    fpga: str
    uart_sn: str
    programming_interface: str
    date: str
    subcontainers: Dict[str, PBlock]

    @classmethod
    def from_hdf5(
        cls, hdf5_group: h5py.Group, read_session_names: list[str],
        filter_even_stripes: bool = False,
        filter_uneven_stripes: bool = False
    ) -> Self:
        """
        Parses this object from a hdf5 subgroup,
        belonging to a experiment hdf5 file
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

        # This is a fix because attribute is named "board_name" instead of
        # name in experiment hdf5
        kwargs["name"] = kwargs["board_name"]
        kwargs.pop("board_name")

        pblocks = {
            key: PBlock.from_hdf5(
                hdf5_group[key], key, read_session_names=read_session_names,
                filter_even_stripes=filter_even_stripes,
                filter_uneven_stripes=filter_uneven_stripes
            )
            for key in hdf5_group
            if "pblock" in key
        }
        bram_count = sum([pblock.bram_count for pblock in pblocks.values()])
        kwargs["bram_count"] = bram_count
        kwargs["subcontainers"] = pblocks
        kwargs["read_session_names"] = read_session_names

        return cls(**kwargs)


@dataclass(frozen=True)
class Experiment(ExperimentContainer):
    """
    See ExperimentContainer
    - Highest layer of ExperimentContainers

    Attributes;
        subcontainer: See ExperimentContainer
        commit: Hash value of git commit used during experiment
    """

    subcontainers: Dict[str, Board]
    commit: str

    @classmethod
    def from_hdf5(cls, hdf5_group: h5py.Group, commit: str,
        filter_even_stripes: bool = False,
        filter_uneven_stripes: bool = False) -> Self:
        """
        Parses this object from a hdf5 subgroup,
        belonging to a experiment hdf5 file
        """
        read_session_names = [
            binary_str.decode()
            for binary_str in hdf5_group["read_session_names"]
        ]

        boards = {
            board: Board.from_hdf5(
                hdf5_group["boards"][board],
                read_session_names=read_session_names,
                filter_even_stripes=filter_even_stripes,
                filter_uneven_stripes=filter_uneven_stripes
            )
            for board in hdf5_group["boards"]
        }
        bram_count = sum([board.bram_count for board in boards.values()])
        return cls(
            name="experiment",
            bram_count=bram_count,
            subcontainers=boards,
            commit=commit,
            read_session_names=read_session_names,
        )
