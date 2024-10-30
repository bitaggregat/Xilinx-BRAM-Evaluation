import random
import statistics
from abc import ABCMeta
from typing import Any, Callable, Self
import h5py
import numpy as np
import numpy.typing as npt
import scipy.stats
from scipy.spatial.distance import hamming
from .experiment_hdf5 import Read, ReadSession, ExperimentContainer
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
        "Maximum": np.max
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
            ]
        )
        meta_statistic_ds.attrs["Column Header"] = self.statistic_method_names

def entropy_list(reads: list[Read]) -> npt.NDArray[np.float64]:
    return np.fromiter((read.entropy for read in reads), np.float64)

def intradistance_bootstrap(reads: list[Read], k:int = 0) -> npt.NDArray[np.float64]:
    distance_values = list()
    for _ in range(len(reads)):
        idx1 = random.randrange(0, len(reads))
        while (idx2 := random.randrange(0, len(reads))) == idx1:
            idx2 = random.randrange(0, len(reads))
        distance_values.append(hamming(reads[idx1].bits_flattened, reads[idx2].bits_flattened))
    return np.array(distance_values)

def interdistance_bootstrap(reads: list[Read], other_reads: list[Read], k: int = 1000) -> npt.NDArray[np.float64]:
    self_choices = [
        choice.bits_flattened for choice in
        random.choices(reads, k=k)
    ]
    other_choices =  [
        choice.bits_flattened for choice in
        random.choices(other_reads, k=k)
    ]
    return np.fromiter(map(hamming, self_choices, other_choices))

class Statistic(HDF5Convertible, metaclass=ABCMeta):
    """
    Statistic over ReadSession
    """
    # TODO Test
    description: str
    stat_func: Callable[[list[Read]], npt.NDArray[np.float64]]
    stat_func_kwargs: dict    # args that are used by method additionally to Reads
    data_read_stat: npt.NDArray[np.float64]
    parity_read_stat: npt.NDArray[np.float64]
    mergable = False

    @property
    def meta_stats(self) -> dict[str, MetaStatistic]:
        return {
            "Data": MetaStatistic(self.data_read_stat),
            "Parity": MetaStatistic(self.parity_read_stat)
        }
        
    def add_to_hdf5_group(self, parent: h5py.Group) -> None:
        statistic_group = parent.create_group(self._hdf5_group_name)

        parity_group = statistic_group.create_group("Parity")
        data_group = statistic_group.create_group("Data")
        meta_stats = self.meta_stats

        meta_stats["Parity"].add_to_hdf5_group(parity_group)
        meta_stats["Data"].add_to_hdf5_group(data_group)

        parity_group.create_dataset("Values", (len(self.parity_read_stat,)), dtype="f8", data=self.parity_read_stat)
        data_group.create_dataset("Values", (len(self.data_read_stat),), dtype="f8", data=self.data_read_stat)

class SimpleStatistic(Statistic, metaclass=ABCMeta):
    mergable = True

    def __init__(self, read_session: ReadSession = None, data_read_stat: Any = None, parity_read_stat: Any = None, stat_func_kwargs: dict[str, Any] = {}) -> None:
        self.stat_func_kwargs = stat_func_kwargs
        if read_session is not None:
            self.data_read_stat = self.stat_func(read_session.data_reads, **stat_func_kwargs)
            self.parity_read_stat = self.stat_func(read_session.parity_reads, **stat_func_kwargs)
        elif data_read_stat is None or parity_read_stat is None:
            raise Exception("Either read_session or data_read_stat and parity_read_stat have to be not None")
        else:
            self.data_read_stat = data_read_stat
            self.parity_read_stat = parity_read_stat


    @classmethod
    def from_merge(cls, stats: list[Self]) -> Self:
        """
        Combines stats by just adding their lists together
        """  
        sample_instance = stats[0]
        if any([not isinstance(obj, cls) for obj in stats]):
            raise Exception("Can't combine non StatisticContatiner types. 'stat' list has to be homogene.")
        else:
            merged_data_read_stat = list()
            merged_parity_read_stat = list()

            for statistic_container in stats:
                merged_data_read_stat.append(statistic_container.data_read_stat)
                merged_parity_read_stat.append(statistic_container.parity_read_stat)

            return cls(
                # This assumes that all subclasses set their description from a default value (without any argument)
                read_session=None,
                data_read_stat=np.array(merged_data_read_stat).flatten(),
                parity_read_stat=np.array(merged_parity_read_stat).flatten(),
                **sample_instance.stat_func_kwargs
            )


class ComparisonStatistic(Statistic, metaclass=ABCMeta):
    """
    Statistic that compares two ReadSessions
    """
    stat_func: Callable[[list[Read], list[Read]], npt.NDArray[np.float64]] = None
    mergable = False

    def __init__(self, read_sessions: list[ReadSession], stat_func_kwargs: dict[str, Any] = {}) -> None:
        self.stat_func_kwargs = stat_func_kwargs
        
        self.compare(read_sessions, **stat_func_kwargs)

    @classmethod
    def from_merge(cls, stats: list[Self]) -> Self:
        raise NotImplementedError
    
    def compare(self, read_sessions: list[ReadSession]) -> None:
        # TODO TEST!
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
                    data_compared_values.append(self.stat_func(
                        read_sessions[idx_i].data_reads,
                        read_sessions[idx_j].data_reads,
                        **self.stat_func_kwargs
                    ))
                    parity_compared_values.append(self.stat_func(
                        read_sessions[idx_i].parity_reads,
                        read_sessions[idx_j].parity_reads,
                        **self.stat_func_kwargs
                    ))
        
        # This combination of using lists of numpy arrays and then flatten them, is not the most efficient.
        # It would be more efficient to allocate a numpy array with zeros and then fill it via slicing.
        # But because of other priorities, such proper implementation is postponed for now
        # TODO improve this implementation if theres spare time
        self.data_read_stat = np.array(data_compared_values).flatten()
        self.parity_read_stat = np.array(parity_compared_values).flatten()

class IntradistanceStatistic(SimpleStatistic):
    """
    TODO: argue if this is good practice:
          pro: 
            hides stat_func, name and type comparison from outer layer
          contra:
            OOP overkill
            more reference calls == slower   
    """
    _hdf5_group_name = "Intradistance"
    description="Intradistance of Bootstrap of set of SUV's via relative Hamming Distance"
    stat_func=staticmethod(intradistance_bootstrap)

class EntropyStatistic(SimpleStatistic):
    """
    TODO: argue if this is good practice:
          pro: 
            hides stat_func, name and type comparison from outer layer
          contra:
            OOP overkill
            more reference calls == slower   
    """
    _hdf5_group_name = "Entropy"
    description="Entropy on single reads via counts of 1's and 0's in SUV"
    stat_func=staticmethod(entropy_list)

class InterdistanceStatistic(ComparisonStatistic):
    """
    TODO: argue if this is good practice:
          pro: 
            hides stat_func, name and type comparison from outer layer
          contra:
            OOP overkill
            more reference calls == slower   
    """
    _hdf5_group_name = "Interdistance"
    description="Interdistance values between Bootstrap of two sets of SUV's"
    stat_func=staticmethod(interdistance_bootstrap)
