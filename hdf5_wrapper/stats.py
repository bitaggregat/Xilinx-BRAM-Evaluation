"""
Module contains classes for objects that produce, store and
visualize statistics over Read's or ReadSession's
"""

import random
from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Self
import h5py
import numpy as np
import numpy.typing as npt
from scipy.spatial.distance import hamming
from .experiment_hdf5 import Read, ReadSession
from .hdf5_convertible import HDF5Convertible


class MetaStatistic(HDF5Convertible):
    """
    Stores stats about stats
    """

    _hdf5_group_name = "Meta Statistic"
    statistic_methods = {
        "Mean": np.mean,
        "Median": np.median,
        "Variance": np.var,
        "StdDeviation": np.std,
        "Minimum": np.min,
        "Maximum": np.max,
    }
    statistic_method_names = sorted(list(statistic_methods.keys()))
    stats: dict[str, float] = None

    def __init__(self, values: npt.NDArray[np.float64]) -> None:
        self.stats = {
            stat_name: method(values)
            for stat_name, method in self.statistic_methods.items()
        }

    def add_to_hdf5_group(self, parent: h5py.Group) -> None:
        meta_statistic_ds = parent.create_dataset(
            self._hdf5_group_name,
            (1, len(self.statistic_method_names)),
            dtype="f8",
            data=[
                self.stats[method_name]
                for method_name in self.statistic_method_names
            ],
        )
        meta_statistic_ds.attrs["Column Header"] = self.statistic_method_names


def entropy_list(reads: list[Read]) -> npt.NDArray[np.float64]:
    """
    Produces list of entropy values (one for each Read object)
    """
    return np.fromiter((read.entropy for read in reads), np.float64)


def intradistance(reads: list[Read]) -> npt.NDArray[np.float64]:
    """
    Produces ((k+1)*k)/2 intradistance values
    (Each Read is compared with each other Read of the list)
    """
    reads_length = len(reads)
    return np.fromiter(
        (
            hamming(reads[i].bits_flattened, reads[j].bits_flattened)
            for i in range(len(reads_length))
            for j in range(i, len(reads_length))
        ),
        np.float64,
    )


def intradistance_bootstrap(
    reads: list[Read], k: int = 10000
) -> npt.NDArray[np.float64]:
    """
    Produces k intradistance values or the maximum, if the maximum of
    possible values (without pair duplicates) is smaller than k

    Pairs of values are chosen pseudo randomly.
    Duplicates can occur

    Less compute time expensive alternative to "intradistance"
    """
    k = int(min(k, (len(reads) ** 2 - len(reads) / 2)))

    return np.fromiter(
        (
            hamming(
                *[
                    read.bits_flattened
                    for read in tuple(random.choices(reads, k=2))
                ]
            )
            for _ in range(k)
        ),
        np.float64,
    )


def interdistance(
    reads: list[Read], other_reads: list[Read]
) -> npt.NDArray[np.float64]:
    """
    Produces l*m interdistance values,
    where l, m are the lengths of "reads" and "other_reads"
    """
    return np.fromiter(
        (
            hamming(read_x.bits_flattened, read_y.bits_flattened)
            for read_x in reads
            for read_y in other_reads
        ),
        np.float64,
    )


def interdistance_bootstrap(
    reads: list[Read], other_reads: list[Read], k: int = 1000
) -> npt.NDArray[np.float64]:
    """
    Produces k interdistance values
    Choses pairs of values from "reads" and "other_reads" pseudo randomly.

    Duplicates can occur

    Less computing tome expensive alternative to "interdistance"
    """
    self_choices = [
        choice.bits_flattened for choice in random.choices(reads, k=k)
    ]
    other_choices = [
        choice.bits_flattened for choice in random.choices(other_reads, k=k)
    ]

    return np.fromiter(map(hamming, self_choices, other_choices))


class Statistic(HDF5Convertible, metaclass=ABCMeta):
    """
    Statistic over ReadSession.
    Abstract class
    """

    description: str
    stat_func: Callable[[list[Read]], npt.NDArray[np.float64]]
    stat_func_kwargs: (
        dict  # Args that are used by method additionally to Reads
    )

    # This class and objects that handle ReadSession data in general
    # Differentiate between two types of Reads (see ReadSession)
    data_stats: npt.NDArray[np.float64]
    parity_stats: npt.NDArray[np.float64]
    mergable = False  # Declares if subclass is allowed to call "from_merge"

    @property
    def meta_stats(self) -> dict[str, MetaStatistic]:
        # We use just in time calculation for this attribute,
        # because it may not always be needed
        return {
            "Data": MetaStatistic(self.data_stats),
            "Parity": MetaStatistic(self.parity_stats),
        }

    def add_to_hdf5_group(self, parent: h5py.Group) -> None:
        statistic_group = parent.create_group(self._hdf5_group_name)

        parity_group = statistic_group.create_group("Parity")
        data_group = statistic_group.create_group("Data")
        meta_stats = self.meta_stats

        meta_stats["Parity"].add_to_hdf5_group(parity_group)
        meta_stats["Data"].add_to_hdf5_group(data_group)

        parity_group.create_dataset(
            "Values",
            (
                len(
                    self.parity_stats,
                )
            ),
            dtype="f8",
            data=self.parity_stats,
        )
        data_group.create_dataset(
            "Values", (len(self.data_stats),), dtype="f8", data=self.data_stats
        )

    @classmethod
    @abstractmethod
    def from_merge(cls, stats: list[Self]) -> Self:
        raise NotImplementedError


class SimpleStatistic(Statistic, metaclass=ABCMeta):
    """
    Statistic over function such that there is one value for each Read.
    e.g. intradistance
    """

    mergable = True

    def __init__(
        self,
        read_session: ReadSession = None,
        data_stats: Any = None,
        parity_stats: Any = None,
        stat_func_kwargs: dict[str, Any] = {},
    ) -> None:
        """
        Class can be created from either:
        - ReadSession
        - already precalculated data and parity stats
        """
        self.stat_func_kwargs = stat_func_kwargs
        if read_session is not None:
            self.data_stats = self.stat_func(
                read_session.data_reads, **stat_func_kwargs
            )
            self.parity_stats = self.stat_func(
                read_session.parity_reads, **stat_func_kwargs
            )
        elif data_stats is None or parity_stats is None:
            raise Exception(
                "Either read_session or data_stats and "
                "parity_stats have to be not None"
            )
        else:
            self.data_stats = data_stats
            self.parity_stats = parity_stats

    @classmethod
    def from_merge(cls, stats: list[Self]) -> Self:
        """
        Combines stats by just adding their lists together.
        This works because statistical values of this class
        are dependant on single Read values
        """
        sample_instance = stats[0]
        if any([not isinstance(obj, cls) for obj in stats]):
            raise Exception(
                "Can't combine non StatisticContatiner types. 'stat' list"
                " has to be homogeneous."
            )
        else:
            merged_data_stats = list()
            merged_parity_stats = list()

            for statistic_container in stats:
                merged_data_stats.append(statistic_container.data_stats)
                merged_parity_stats.append(statistic_container.parity_stats)

            return cls(
                # This assumes that all subclasses set their description
                # from a default value (without any argument)
                read_session=None,
                data_stats=np.array(merged_data_stats).flatten(),
                parity_stats=np.array(merged_parity_stats).flatten(),
                **sample_instance.stat_func_kwargs,
            )


class ComparisonStatistic(Statistic, metaclass=ABCMeta):
    """
    Statistic that compares two ReadSessions.
    e.g. interdistance

    This type of Statistic is not mergable,
    because their values depend on pairs of values.
    These pairs would change drastically
    when addtional values (merge) would be added
    """

    stat_func: Callable[[list[Read], list[Read]], npt.NDArray[np.float64]] = (
        None
    )
    mergable = False

    def __init__(
        self,
        read_sessions: list[ReadSession],
        stat_func_kwargs: dict[str, Any] = {},
    ) -> None:
        self.stat_func_kwargs = stat_func_kwargs

        self.compare(read_sessions, **stat_func_kwargs)

    def compare(self, read_sessions: list[ReadSession]) -> None:
        """
        Produces ((k+1)*k)/2 pairs of ReadSession's
        Calls stat_func over each pair and gathers the produced values
        """
        data_compared_values = list()
        parity_compared_values = list()

        # It may become to expensive to do this n*n,
        # if so replace n*n with n bootstrap choices
        for idx_i in range(len(read_sessions)):
            for idx_j in range(len(read_sessions)):
                if idx_i == idx_j:
                    # Don't compare ReadSession with itself
                    continue
                else:
                    data_compared_values.append(
                        self.stat_func(
                            read_sessions[idx_i].data_reads,
                            read_sessions[idx_j].data_reads,
                            **self.stat_func_kwargs,
                        )
                    )
                    parity_compared_values.append(
                        self.stat_func(
                            read_sessions[idx_i].parity_reads,
                            read_sessions[idx_j].parity_reads,
                            **self.stat_func_kwargs,
                        )
                    )

        # This combination of using lists of numpy arrays and then flattening
        # them, is not the most efficient.
        # It would be more efficient to allocate a numpy array with zeros
        # and then fill it via slicing.
        # But because of other priorities,
        # such proper implementation is postponed for now
        # TODO improve this implementation if theres spare time
        self.data_stats = np.array(data_compared_values).flatten()
        self.parity_stats = np.array(parity_compared_values).flatten()


class IntradistanceStatistic(SimpleStatistic):
    _hdf5_group_name = "Intradistance"
    description = "Intradistance of Bootstrap of set of SUV's"
    "via relative Hamming Distance"
    stat_func = staticmethod(intradistance_bootstrap)
    stat_func_kwargs = {"k": 10000}


class EntropyStatistic(SimpleStatistic):
    _hdf5_group_name = "Entropy"
    description = "Entropy on single reads via counts of 1's and 0's in SUV"
    stat_func = staticmethod(entropy_list)


class InterdistanceStatistic(ComparisonStatistic):
    _hdf5_group_name = "Interdistance"
    description = "Interdistance values between Bootstrap of two sets of SUV's"
    stat_func = staticmethod(interdistance_bootstrap)
    stat_func_kwargs = {"k": 100000}
