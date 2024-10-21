from typing import Callable, Any, Self
from .experiment_hdf5 import Read, ReadSession, BramBlock, PBlock, Board, Experiment
import random
from scipy.spatial.distance import hamming
from dataclasses import dataclass, field
import statistics
from itertools import combinations
import numpy as np
import math
from enum import Enum
import h5py

# TODO to much code for single file -> split up into multiple files

class StatisticMethod:
    """
    Makes it easier to iterate over all relevant stat methods,
    without using a singleton dict
    """
    statistic_methods = {
        "Mean": statistics.mean,
        "Median": statistics.median,
        "Variance": statistics.variance,
        "StdDeviation": statistics.stdev,
        "Minimum": min,
        "Maximum": max
    }
    

class MultiReadSessionOwner:
    # TODO minimal test
    """
    Class that manages reads of multiple read sessions
    """
    _read_session_names: list[str] = None

    @property
    def read_session_names(self) -> list[str]:
        """
        All read_session owners need to know the names of their read sessions
        These names are used as identifiers/dict keys
        """
        if self._read_session_names is None:
            raise Exception("_read_session_names are not set.")
        else:
            return self._read_session_names
        
class HDF5Convertible(MultiReadSessionOwner):
    """
    Alot of the HDF5 conversion/write code is repetitive
    This class provides functions for typical cases of conversion to hdf5,
        in order to reduce code duplicates
    Note: This class may be replaceable by functions (TODO debate)
    """
    # Names of attributes that use ReadSessionListStat
    list_stats: list[str]
    substats: list

    def add_list_stats_to_hdf5_group(self, parent: h5py.Group) -> None:
        # TODO Test
        if self.list_stats is None:
            raise Exception("Attribute 'list_stats' has to be initialized before using this function")
        else:
            for list_stat_name in self.list_stats:
                stat_group = parent.create_group(list_stat_name)
                list_stat = getattr(self, list_stat_name)
                meta_stat_lines = list()
                meta_stat_read_session_header = []
                for read_session_name in self.read_session_names:
                    if not list_stat[read_session_name] or list_stat[read_session_name] is None:
                        continue
                    else:
                        read_session_group = stat_group.create_group(read_session_name)
                        read_session_group.create_dataset("data_bits", (len(list_stat[read_session_name].data_read_stat),), "f8", list_stat[read_session_name].data_read_stat)
                        read_session_group.create_dataset("parity_bits", (len(list_stat[read_session_name].parity_read_stat),), "f8", list_stat[read_session_name].parity_read_stat)
                        meta_stat_read_session_header.append(read_session_name)
                        meta_stat_lines.append([
                            list_stat[read_session_name].meta_stats[stat_method_name]
                            for stat_method_name in list_stat[read_session_name].meta_stats
                            ])
                if meta_stat_lines:
                    meta_stat_dataset = stat_group.create_dataset("meta_stats", (len(list_stat),len(StatisticMethod.statistic_methods) * 2), "f8", meta_stat_lines)
                    meta_stat_dataset.attrs["read_sessions"] = meta_stat_read_session_header
                    meta_stat_dataset.attrs["statistic_methods"] = [method_name for method_name in list_stat[self.read_session_names[0]].meta_stats]
                else: 
                    continue
    
    def add_stat_to_hdf5_group(self, parent: h5py.Group, name: str, stat) -> None:
        header = [read_session_name for read_session_name in self.read_session_names]
        dataset = parent.create_dataset(name, (len(stat),), "f8", [stat[read_session_name] for read_session_name in self.read_session_names])
        dataset.attrs["read_session"] = header


def entropy_list(reads: list[Read]) -> list[float]:
    # TODO Test
    return [read.entropy for read in reads]

def intradistance_bootstrap(reads: list[Read], k: int) -> list[float]:
    # TODO Test
    distance_values = list()
    for _ in range(len(reads)):
        idx1 = random.randrange(0, len(reads))
        while (idx2 := random.randrange(0, len(reads))) == idx1:
            idx2 = random.randrange(0, len(reads))
        distance_values.append(hamming(reads[idx1].bits_flatted, reads[idx2].bits_flatted))
    return distance_values

def interdistance_bootstrap(reads: list[Read], other_reads: list[Read], k: int) -> list[float]:
    # TODO Test
    self_choices = [
        choice.bits_flatted for choice in
        random.choices(reads, k=k)
    ]
    other_choices =  [
        choice.bits_flatted for choice in
        random.choices(other_reads, k=k)
    ]
    return map(hamming, self_choices, other_choices)


@dataclass(init=False)
class ReadSessionStat:
    # TODO Test
    description: str
    generation_func: Callable
    data_read_stat: Any
    parity_read_stat: Any

    def __init__(self, description: str, generation_func: Callable, read_session: ReadSession = None, data_read_stat: Any = None, parity_read_stat: Any = None, k: int = None) -> None:
        self.description = description
        self.generation_func = generation_func
        if read_session is not None:
            if k is not None:
                self.data_read_stat = self.generation_func(read_session.data_reads, k)
                self.parity_read_stat = self.generation_func(read_session.parity_reads, k)
            else:        
                self.data_read_stat = self.generation_func(read_session.data_reads)
                self.parity_read_stat = self.generation_func(read_session.parity_reads)
        elif data_read_stat is None or parity_read_stat is None:
            raise Exception("Either read_session or data_read_stat and parity_read_stat have to be not None")
        else:
            self.data_read_stat = data_read_stat
            self.parity_read_stat = parity_read_stat

def generate_meta_stats(values: list[float], prefix: str = "") -> dict[str, float]:
    # TODO TEst
    """
    Arguments:
        prefix: string that is prefix in every key of created dict
    """
    return {
        f"{prefix} {method_name}": method(values)
        for method_name, method in StatisticMethod.statistic_methods.items()
    }

@dataclass(init=False)
class ReadSessionListStat(ReadSessionStat):
    # TODO Test
    data_read_stat: list[float]
    parity_read_stat: list[float]
    _meta_stats: dict[str, float] = field(init=False, default_factory=dict, repr=False)

    def __init__(self, description: str, generation_func: Callable, read_session: ReadSession = None, data_read_stat: Any = None, parity_read_stat: Any = None, k: int = None) -> None:
        super().__init__(description, generation_func, read_session, data_read_stat, parity_read_stat, k)
        self._meta_stats = dict()

    @property
    def meta_stats(self) -> dict[str, float]:
        return {
            **self._meta_stats, 
            **generate_meta_stats(self.data_read_stat, "Data"),
            **generate_meta_stats(self.parity_read_stat, "Parity")
        }

    def __add__(self, other: Self) -> Self:
        if self.description != other.description or self.generation_func != other.generation_func:
            raise Exception(f"Can't add ReadSessionsStats with different generation_func's: {self.generation_func} and {other.generation_func}")
        
        return ReadSessionListStat(
            self.description,
            self.generation_func,
            None,
            self.data_read_stat + other.data_read_stat,
            self.parity_read_stat + other.parity_read_stat
        )
    
    def __radd__(self, other):
        """
        This needs to be defined in order to use sum() on a list of ReadSessionListStat objects
        """
        if other == 0:
            return self
        else:
            return self.__add__(other)


class StatAggregator(MultiReadSessionOwner):
    # TODO Test
    '''
    Class that provides aggregate_substats function
    '''
    substats: list = None
    # List of names of attributes that are aggregatable
    aggregatable_stats: list[str] = None

    def aggregate_substats(self) -> None:
        '''
        Class is expected to have a list of substat objects
            e.g. PblockStat has list[BramStat]
        This aggregates these substats in order gain knowledge of the stat on a meta lvl
            - e.g. we know the median entropy of each bram block,
              -> now we want to know the median entropy of ALL bram blocks combined
        '''
        if self.aggregatable_stats is None:
            raise Exception("List 'aggregatable_stats' needs to be set to use this function")
        elif self.substats is None:
            raise Exception("List 'substats' needs to be set to use this function")
        else:
            attribute_references = {
                attr_name: getattr(self, attr_name)
                for attr_name in self.aggregatable_stats
            }
                
            for read_session_name in self.read_session_names:
                attribute_temp_aggregation_lists = {
                    attr_name: list()
                    for attr_name in self.aggregatable_stats
                }

                for substat in self.substats:
                    for attr_name in self.aggregatable_stats:
                        attribute_temp_aggregation_lists[attr_name].append(
                            getattr(substat, attr_name)[read_session_name]
                        )
                
                # This uses the "+" operator on ReadSessionListStat objects,
                # which works because the ReadSessionListStat has a custom implementation of "__add__" and "__radd__"
                for attr_name in self.aggregatable_stats:
                    # List is potentially empty:
                    # - e.g. when only 1 BramBlock was measured, no interdistance can be calculated
                    if attribute_temp_aggregation_lists[attr_name][0]:
                        attribute_references[attr_name][read_session_name] = sum(attribute_temp_aggregation_lists[attr_name])
                    else:
                        attribute_references[attr_name][read_session_name] = None


@dataclass(init=False)
class BramBlockStat(HDF5Convertible):
    # TODO Test
    name: str = field(init=False)
    intradistance: dict[str, ReadSessionListStat]
    entropy: dict[str, ReadSessionListStat]

    def __init__(self, bram_block: BramBlock, read_session_names: list[str], k: int) -> None:
        self._read_session_names = read_session_names
        self.list_stats = ["intradistance", "entropy"]
        self.name = bram_block.name
        self.intradistance = dict()
        self.entropy = dict()
        for read_session_name in read_session_names:
            self.intradistance[read_session_name] = ReadSessionListStat(
                f"intradistance_{read_session_name}",
                intradistance_bootstrap,
                bram_block.read_sessions[read_session_name],
                k=k
            )
            self.entropy[read_session_name] = ReadSessionListStat(
                f"entropy_{read_session_name}",
                entropy_list,
                bram_block.read_sessions[read_session_name]
            )

    def add_to_hdf5_group(self, parent: h5py.Group) -> None:
        bram_block_group = parent.create_group(self.name)

        self.add_list_stats_to_hdf5_group(bram_block_group)

@dataclass(init=False)
class PblockStat(StatAggregator, HDF5Convertible):
    # TODO Test
    name: str = field(init=False)
    bram_block_stats: list[BramBlockStat] = field(init=False)
    intradistance: dict[str, ReadSessionListStat] = field(init=False)
    entropy: dict[str, ReadSessionListStat] = field(init=False)
    bram_interdistance: dict[str, ReadSessionListStat] = field(init=False)

    def __init__(self, pblock: PBlock, read_session_names: list[str], k: int) -> None:
        self._read_session_names = read_session_names
        self.aggregatable_stats = ["intradistance", "entropy"]
        self.name = pblock.name
        self.intradistance = dict()
        self.entropy = dict()
        self.bram_interdistance = dict()
        self.bram_block_stats = [
            BramBlockStat(bram_block, read_session_names, k)
            for bram_block in pblock.bram_blocks.values()
        ]
        self.substats = self.bram_block_stats
        self.list_stats = ["intradistance", "entropy", "bram_interdistance"]
        self.aggregate_substats()

        #############################
        # Create interdistance values
        bram_combinations_idx = [
            tuple(combination)
            for combination in
            combinations(range(len(self.bram_block_stats)), 2)
        ]
        bram_block_list = list(pblock.bram_blocks.values())
        self.bram_interdistance = dict()
        for read_session_name in self.read_session_names:
            self.bram_interdistance[read_session_name] = [
                ReadSessionListStat(
                    "bram_interdistance",
                    interdistance_bootstrap,
                     data_read_stat=interdistance_bootstrap(
                         bram_block_list[idx1].data_reads,
                         bram_block_list[idx2].parity_reads,
                         k
                     ),
                     parity_read_stat=interdistance_bootstrap(
                         bram_block_list[idx1].data_reads,
                         bram_block_list[idx2].parity_reads,
                         k
                     )
                )
                for idx1, idx2 in bram_combinations_idx
            ]
        # End of interdistance value creation
        ####################################

    def add_to_hdf5_group(self, parent: h5py.Group) -> None:
        pblock_group = parent.create_group(self.name)

        self.add_list_stats_to_hdf5_group(pblock_group)

        # Create bram stats
        multi_bram_block_group = pblock_group.create_group("bram_blocks")
        for bram_block_stat in self.bram_block_stats:
            bram_block_stat.add_to_hdf5_group(multi_bram_block_group)


@dataclass(init=False)
class BoardStat(StatAggregator, HDF5Convertible):
    # TODO Test
    board_name: str = field(init=False)
    pblock_stats: list[PblockStat] = field(init=False)
    intradistance: dict[str, ReadSessionListStat] = field(init=False)
    entropy: dict[str, ReadSessionListStat] = field(init=False)
    bram_interdistance: dict[str, ReadSessionListStat] = field(init=False)

    def __init__(self, board: Board, read_session_names: list[str], k: int) -> None:
        self._read_session_names = read_session_names
        self.aggregatable_stats = ["intradistance", "entropy", "bram_interdistance"]
        self.board_name = board.board_name
        self.intradistance = dict()
        self.entropy = dict()
        self.bram_interdistance = dict()
        self.pblock_stats = [
            PblockStat(pblock, read_session_names, k)
            for pblock in board.pblocks.values()
        ]
        self.substats = self.pblock_stats
        self.list_stats = ["intradistance", "entropy", "bram_interdistance"]

        self.aggregate_substats()

        # TODO debate whether or not interdistance between pblocks is useful knowledge

    def add_to_hdf5_group(self, parent: h5py.Group) -> None:
        board_group = parent.create_group(self.board_name)

        self.add_list_stats_to_hdf5_group(board_group)

        # Create bram stats
        multi_pblock_group = board_group.create_group("pblocks")
        for pblock_stat in self.pblock_stats:
            pblock_stat.add_to_hdf5_group(multi_pblock_group)


@dataclass(init=False)
class ExperimentStat(StatAggregator, HDF5Convertible):
    # TODO Test
    board_stats: list[BoardStat] = field(init=False)
    intradistance: dict[str, ReadSessionListStat] = field(init=False)
    entropy: dict[str, ReadSessionListStat] = field(init=False)
    bram_interdistance: dict[str, ReadSessionListStat] = field(init=False)

    def __init__(self, experiment: Experiment, k: int) -> None:
        read_session_names = experiment.read_session_names
        self._read_session_names = read_session_names
        self.intradistance = dict()
        self.entropy = dict()

        self.bram_interdistance = dict()

        self.board_stats = [
            BoardStat(board, read_session_names, k)
            for board in experiment.boards.values()
        ]
        self.substats = self.board_stats
        self.list_stats = ["intradistance", "entropy", "bram_interdistance"]

        self.aggregatable_stats = ["intradistance", "entropy", "bram_interdistance"]
        self.aggregate_substats()

        # TODO debate whether or not interdistance between devices is useful knowledge

    def add_to_hdf5_group(self, parent: h5py.Group) -> None:

        self.add_list_stats_to_hdf5_group(parent)

        # Create bram stats
        multi_board_group = parent.create_group("boards")
        for board_stat in self.board_stats:
            board_stat.add_to_hdf5_group(multi_board_group)
