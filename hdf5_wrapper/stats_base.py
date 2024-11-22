"""
Module contains classes for objects that produce, store and
visualize statistics over Read's or ReadSession's
"""

from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Any, Callable, Self
import h5py
import numpy as np
import numpy.typing as npt
from .experiment_hdf5 import Read, ReadSession
from .interfaces import HDF5Convertible, Plottable
from .utility import PlotSettings

class MetaStatistic(HDF5Convertible, Plottable):
    """
    Stores stats about stats

    Attributes:
        _hdf5_group_name: See HDF5Convertible
        statistic_methods: Statistic functions mapped by a sttring that shall
                            represent them
        statistic_method_names: Sorted list of keys of "statistic_methods"
        stats: Results of statistic functions mapped by their functions name
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
    stats: dict[str, np.float64] = None
    bit_type: str

    def __init__(
        self,
        values: npt.NDArray[np.float64],
        plot_settings: PlotSettings,
        bit_type: str
    ) -> None:
        super().__init__(plot_settings)
        self.stats = {
            stat_name: method(values)
            for stat_name, method in self.statistic_methods.items()
        }
        self.bit_type = bit_type

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

    def meta_stat_latex_table(self, path: Path) -> None:
        header = " & ".join(
            [
                "\\textbf{" + stat_name.replace("_", "\_") + "}"
                for stat_name in self.statistic_method_names
            ]
        )
        table_format = "|".join(["c"] * len(self.statistic_method_names))
        row = " & ".join(
            [
                str(self.stats[stat_name])
                for stat_name in self.statistic_method_names
            ]
        )
        with open(path.with_suffix(".tex"), mode="w") as f:
            f.writelines(
                [
                    "\\begin{tabular}{" + table_format + "}\n",
                    header + "\\\\\n",
                    "\\hline\n",
                    row + "\\\\\n",
                    "\\end{tabular}\n",
                ]
            )

    def _plot(self) -> None:
        self.meta_stat_latex_table(Path(self.plot_settings.path, f"{self.bit_type}_meta_stats"))


class Statistic(HDF5Convertible, Plottable, metaclass=ABCMeta):
    """
    Statistic over ReadSession.
    Abstract class

    Attributes:
        description: String that helps identifying the statistic used
        stat_func: Function used to create statistic
        stat_func_kwargs: Kwargs of additinal parameters for "stat_func"
        data_stats: Stats of data bits, gained through "stat_func"
        parity_stats: Stats of parity bits, gained through "stat_func"
        mergable: Indicates if "from_merge" method can be used on multiple
                    instances of this "Statistic" class
    """

    description: str
    stat_func: Callable[[list[Read]], npt.NDArray[np.float64]]
    stat_func_kwargs: dict = dict()  # Args that are used by method additionally to Reads

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
            "Data": MetaStatistic(
                self.data_stats,
                self.plot_settings.with_expanded_path(""),
                bit_type="data"
            ),
            "Parity": MetaStatistic(
                self.parity_stats,
                self.plot_settings.with_expanded_path(""),
                bit_type="parity"
            ),
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
    def from_merge(cls, stats: list[Self], plot_settings: PlotSettings) -> Self:
        raise NotImplementedError

    def _plot(self) -> None:
        meta_stats = self.meta_stats
        for bit_type in ["Data", "Parity"]:
            meta_stats[bit_type].plot()


class SimpleStatistic(Statistic, metaclass=ABCMeta):
    """
    Statistic over function such that there is one value for each Read.
    e.g. intradistance

    Attributes:
        mergable: See Statistic. Instances of this class are mergable.
    """

    mergable = True

    def __init__(
        self,
        plot_settings: PlotSettings,
        read_session: ReadSession = None,
        data_stats: Any = None,
        parity_stats: Any = None
    ) -> None:
        """
        Class can be created from either:
        - ReadSession
        - already precalculated data and parity stats
        """
        self.plot_settings = plot_settings
        if read_session is not None:
            self.data_stats = self.stat_func(
                read_session.data_reads, **self.stat_func_kwargs
            )
            self.parity_stats = self.stat_func(
                read_session.parity_reads, **self.stat_func_kwargs
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
    def from_merge(cls, stats: list[Self], plot_settings: PlotSettings) -> Self:
        """
        Combines stats by just adding their lists together.
        This works because statistical values of this class
        are dependant on single Read values
        """
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
                plot_settings=plot_settings
            )
        

class BitwiseStatistic(SimpleStatistic, metaclass=ABCMeta):
    """
    Statistic where a value is generated for each bit.
    - e.g. probability that bit flips to 1

    The attributes data_read_stat, parity_read_stat are seen as arrays of stats per bit in this case, 
    where the idx is equal to the bit idx inside a BRAM
    """
    mergable = True

    def __init__(self, read_session: ReadSession = None, data_read_stat: Any = None, parity_read_stat: Any = None, stat_func_kwargs: dict[str, Any] = {}) -> None:
        super().__init__(read_session, data_read_stat, parity_read_stat, stat_func_kwargs)
        if len(self.data_stats) != 4096 * 8 or len(self.parity_stats) != 4096:
            raise Exception("Unexpected length for data/parity_read_stat in BitwiseStatistic")
        

    @classmethod
    def from_merge(cls, stats: list[Self]) -> Self:
        """
        Combines stats by adding each value in their lists (like adding two vectors)
        """
        data_read_stats_list = [bitwise_statistic.data_read_stat for bitwise_statistic in stats]
        parity_read_stats_list = [bitwise_statistic.parity_read_stat for bitwise_statistic in stats]

        data_read_stats_sum = list(map(sum, zip(*data_read_stats_list)))

        divide_function = lambda x: float(x/len(stats))
        new_data_read_stats = list(map(divide_function, data_read_stats_sum))
        parity_read_stats_sum = list(map(sum, zip(*parity_read_stats_list)))
        new_parity_read_stats = list(map(divide_function, parity_read_stats_sum))

        return cls(None, new_data_read_stats, new_parity_read_stats)



class ComparisonStatistic(Statistic, metaclass=ABCMeta):
    """
    Statistic that compares two ReadSessions.
    e.g. interdistance

    This type of Statistic is not mergable,
    because their values depend on pairs of values.
    These pairs would change drastically
    when addtional values (merge) would be added

    Attributes:
        stat_func: See Statistic. Method signature differs slightly from 
                    parent class
        mergable: See Statistic. Instances of this class are not mergable
    """

    stat_func: Callable[[list[Read], list[Read]], npt.NDArray[np.float64]] = (
        None
    )
    mergable = False

    def __init__(
        self,
        read_sessions: list[ReadSession],
        plot_settings: PlotSettings
    ) -> None:
        self.plot_settings = plot_settings

        self.compare(read_sessions)

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

    @classmethod
    def from_merge(cls, stats: list[Self], plot_settings: PlotSettings) -> Self:
        return super().from_merge(stats, plot_settings)
