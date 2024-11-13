"""
Module contains Statistic container objects.
These classes encapsulate iterations and handling of Statistic objects.
"""

from abc import ABCMeta
from dataclasses import dataclass, field
from pathlib import Path
from typing import Self, Type
import h5py
from .experiment_hdf5 import ExperimentContainer
from .interfaces import HDF5Convertible, Plottable
from .stats_base import (
    MetaStatistic,
    Statistic,
    SimpleStatistic,
    ComparisonStatistic,
)
from .stats import (
    InterdistanceStatistic,
    IntradistanceStatistic,
    EntropyStatistic,
    BitStabilizationStatistic,
)


@dataclass
class MultiReadSessionMetaStatistic(HDF5Convertible, Plottable):
    """
    Gathers MetaStatistic's of different ReadSessions
    Main objective:
    -> encapsulating the unification of MetaStatistic's
       and their handling in hdf5
    """

    data_meta_statistics: dict[str, MetaStatistic]
    parity_meta_statistics: dict[str, MetaStatistic]
    _read_session_names: list[str]
    _hdf5_group_name: str = field(init=False, default="Meta Statistic")

    def __post_init__(self) -> None:
        # Simple check to help securing the produced datas correctness
        # This may cost some extra time,
        # but it is worth it because correctness is our highest priority
        if (
            any(
                [
                    read_session_name not in self.data_meta_statistics
                    for read_session_name in self._read_session_names
                ]
            )
            or any(
                [
                    read_session_name not in self.parity_meta_statistics
                    for read_session_name in self._read_session_names
                ]
            )
            or len(self.parity_meta_statistics)
            != len(self._read_session_names)
        ):
            raise Exception(
                "Unequal Read Session Names found please inspect via debugger"
            )

    def add_to_hdf5_group(self, parent: h5py.Group) -> None:
        parity_meta_stat_rows = list()
        data_meta_stat_rows = list()
        row_header = list()
        for read_session_name in self._read_session_names:
            # Add meta_stats to list for overview dataset in super group
            parity_meta_stat_rows += [
                self.parity_meta_statistics[read_session_name].stats[
                    statistic_method
                ]
                for statistic_method in MetaStatistic.statistic_method_names
            ]
            data_meta_stat_rows += [
                self.data_meta_statistics[read_session_name].stats[
                    statistic_method
                ]
                for statistic_method in MetaStatistic.statistic_method_names
            ]
            row_header.append(read_session_name)

        parity_meta_ds = parent.create_dataset(
            "Parity Meta Stats",
            (len(row_header), len(MetaStatistic.statistic_methods)),
            dtype="f8",
            data=parity_meta_stat_rows,
        )
        parity_meta_ds.attrs["Column Header"] = (
            MetaStatistic.statistic_method_names
        )
        parity_meta_ds.attrs["Row Header"] = row_header

        data_meta_ds = parent.create_dataset(
            "Data Meta Stats",
            (len(row_header), len(MetaStatistic.statistic_methods)),
            dtype="f8",
            data=data_meta_stat_rows,
        )
        data_meta_ds.attrs["Column Header"] = (
            MetaStatistic.statistic_method_names
        )
        data_meta_ds.attrs["Row Header"] = row_header

    def multi_meta_stat_latex_table(
        self, meta_stats_per_read_session: dict[str, MetaStatistic], path: Path
    ) -> None:
        header = " & " + " & ".join(
            [
                "\\textbf{" + stat_name + "}"
                for stat_name in MetaStatistic.statistic_method_names
            ]
        )
        table_format = "|c||" + "|".join(
            ["c"] * len(MetaStatistic.statistic_method_names)
        )

        rows = [
            " & ".join(
                [read_session_name]
                + [
                    meta_stat.stats[stat_name]
                    for stat_name in MetaStatistic.statistic_method_names
                ]
            )
            + "\\\\"
            for read_session_name, meta_stat in meta_stats_per_read_session.items()
        ]
        with open(path.with_suffix("tex"), mode="w") as f:
            f.writelines(
                [
                    "\\begin{tabular}{" + table_format + "}",
                    header + "\\\\",
                    "\\hline",
                ]
                + rows
                + ["\\end{tabular}"]
            )

    def _plot(self) -> None:
        for bit_meta_stat, bit_type in [
            (self.data_meta_statistics, "data"),
            (self.parity_meta_statistics, "parity"),
        ]:
            self.multi_meta_stat_latex_table(
                bit_meta_stat, Path(self._plot_path, f"{bit_type}_meta_stats")
            )


@dataclass
class MultiReadSessionStatistic(HDF5Convertible, Plottable):
    """
    Gathers Statistics of different ReadSessions but same "Statistic"-type
    - e.g. "IntraDistance"-objects of ReadSessions "previous_value_00"
      and "previous_value_ff"
    """

    statistics: dict[str, Statistic]
    statistic_type: Type[Statistic]
    _read_session_names: list[str]

    def __post_init__(self) -> None:
        if any(
            [
                not isinstance(statistic, self.statistic_type)
                for statistic in self.statistics.values()
            ]
        ):
            raise Exception(
                f"Statistic's are not all of type: {self.statistic_type}"
            )
        self._hdf5_group_name = self.statistic_type._hdf5_group_name

    @property
    def meta_stats(self) -> MultiReadSessionMetaStatistic:
        """
        Just in time processing of meta_stats
        """
        parity_meta_stats = dict()
        data_meta_stats = dict()

        for read_session_name in self._read_session_names:
            parity_meta_stats[read_session_name] = self.statistics[
                read_session_name
            ].meta_stats["Parity"]
            data_meta_stats[read_session_name] = self.statistics[
                read_session_name
            ].meta_stats["Data"]

        return MultiReadSessionMetaStatistic(
            data_meta_stats, parity_meta_stats, self._read_session_names
        )

    @classmethod
    def from_merge(
        cls,
        multi_rs_statistics: list[Self],
        statistic_type: Type[Statistic],
        read_session_names: list[str],
    ) -> Self:
        """
        See SimpleStatistic.from_merge
        """
        if not statistic_type.mergable:
            raise Exception(
                f"Can't merge Statistic objects of type: {statistic_type}"
            )
        statistics = {
            read_session_name: statistic_type.from_merge(
                [
                    multi_rs_statistic.statistics[read_session_name]
                    for multi_rs_statistic in multi_rs_statistics
                ]
            )
            for read_session_name in read_session_names
        }
        return cls(statistics, statistic_type, read_session_names)

    def add_to_hdf5_group(self, parent: h5py.Group) -> None:
        multi_group = parent.create_group(self._hdf5_group_name)
        for read_session_name in self._read_session_names:
            read_session_group = multi_group.create_group(read_session_name)
            self.statistics[read_session_name].add_to_hdf5_group(
                read_session_group
            )
        self.meta_stats.add_to_hdf5_group(multi_group)


class MultiStatisticOwner(HDF5Convertible, Plottable, metaclass=ABCMeta):
    """
    Class that manages MultReadSessionObjects of different Statistic types.
    This is the Statistic container equivalent of a BramBlock object.
    -> It manages Stats (but doesn't manage other Statistic container objects)
    """

    name: str
    _read_session_names: list[str] = None
    statistics: dict[Type[Statistic], MultiReadSessionStatistic]
    types_of_statistics: list[
        Type[Statistic]
    ]  # Needs to be set by child class statically

    def __init__(
        self,
        experiment_container: ExperimentContainer,
        _plot_path: Path,
        _plot_active: bool,
    ) -> None:
        super().__init__(_plot_path, _plot_active)
        self._read_session_names = experiment_container.read_session_names
        self.name = experiment_container.name
        self.statistics = dict()
        self.compute_stats(experiment_container)

    def compute_stats(self, experiment_container: ExperimentContainer) -> None:
        for statistic_type in self.types_of_statistics:
            if issubclass(statistic_type, SimpleStatistic):
                statistics_per_read_session = dict()
                for read_session_name in self._read_session_names:
                    statistics_per_read_session[read_session_name] = (
                        statistic_type(
                            experiment_container.read_sessions[
                                read_session_name
                            ]
                        )
                    )
                self.statistics[statistic_type] = MultiReadSessionStatistic(
                    _plot_path=self._plot_path,
                    _plot_active=self._plot_active,
                    statistics=statistics_per_read_session,
                    statistic_type=statistic_type,
                    _read_session_names=self._read_session_names
                )

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

    def add_to_hdf5_group(self, parent: h5py.Group) -> h5py.Group:
        multi_stat_group = parent.create_group(self.name)

        for statistic_type in self.types_of_statistics:
            if self.statistics[statistic_type]:
                self.statistics[statistic_type].add_to_hdf5_group(
                    multi_stat_group
                )
            else:
                continue

        return multi_stat_group


class StatAggregator(MultiStatisticOwner, metaclass=ABCMeta):
    """
    Class for objects that
    manage multiple MultiStatisticOwner's (called substats)
    Provides aggregation functions for substats.

    Is the Statistic equivalent of PBlock or
    Board objects of "experiment.hdf5.py".
    The main objective of these classes is to reduce repetitive code duplicates
    """

    subowners: list[MultiStatisticOwner] = None
    subowner_type: Type[MultiStatisticOwner]
    subowner_identifier: str  # Needs to be set by child class

    def __init__(
        self,
        experiment_container: ExperimentContainer,
        _plot_path: Path,
        _plot_active,
    ) -> None:
        super().__init__(
            experiment_container=experiment_container,
            _plot_path=_plot_path,
            _plot_active=_plot_active,
        )
        self._read_session_names = experiment_container.read_session_names
        self.name = experiment_container.name
        self.statistics = dict()
        self.subowners = [
            self.subowner_type(subcontainer)
            for subcontainer in experiment_container.subcontainers.values()
        ]
        self.merge_substats()
        self.compare_substats(experiment_container)

    def merge_substats(self) -> None:
        """
        Uses "from_merge" interface from substats (if "mergable")

        Class is expected to have a list of substat objects
            e.g. PblockStat has list[BramStat]
        This method merges these substats in order gain knowledge
        of the stat on a meta lvl
            - e.g. we know the median entropy of each bram block,
              -> we want to know the median entropy of ALL bram blocks combined
        """
        if self.subowners is None or not self.subowners:
            raise Exception(
                "Cannot merge substats because 'subowners' is empty or None"
            )
        else:
            for statistic_type in self.types_of_statistics:
                subowner_sample = self.subowners[0]

                if (
                    statistic_type.mergable
                    and statistic_type in subowner_sample.statistics
                ):
                    self.statistics[statistic_type] = dict()

                    substats = [
                        subowner.statistics[statistic_type]
                        for subowner in self.subowners
                    ]
                    self.statistics[statistic_type] = (
                        MultiReadSessionStatistic.from_merge(
                            substats, statistic_type, self.read_session_names
                        )
                    )

    def compare_substats(
        self, experiment_container: ExperimentContainer
    ) -> None:
        """
        Uses "compare" of substats (if available)
        """
        if self.subowners is None or not self.subowners:
            raise Exception(
                "Cannot compare substats because 'subowners' is empty or None"
            )
        else:
            for statistic_type in self.types_of_statistics:
                if issubclass(statistic_type, ComparisonStatistic):
                    self.statistics[statistic_type] = dict()
                    for read_session_name in self.read_session_names:
                        # Gather read_sessions of same read_session_name
                        # for each container
                        read_sessions_per_container = [
                            subcontainer.read_sessions[read_session_name]
                            for subcontainer in experiment_container.subcontainers.values()
                        ]
                        if len(read_sessions_per_container) == 1:
                            print(
                                "Couldn't compare data of different instances"
                                f" of {statistic_type} because only one "
                                "sample was present"
                            )
                        else:
                            self.statistics[statistic_type][
                                read_session_name
                            ] = statistic_type(read_sessions_per_container)

    def add_to_hdf5_group(self, parent: h5py.Group) -> h5py.Group:
        multi_stat_group = super().add_to_hdf5_group(parent)
        subowner_group = multi_stat_group.create_group(
            self.subowner_identifier
        )
        for subowner in self.subowners:
            subowner.add_to_hdf5_group(subowner_group)


class BramBlockStat(MultiStatisticOwner):
    types_of_statistics = [
        IntradistanceStatistic,
        EntropyStatistic,
        BitStabilizationStatistic,
    ]


class PBlockStat(StatAggregator):
    types_of_statistics = [
        IntradistanceStatistic,
        EntropyStatistic,
        InterdistanceStatistic,
    ]
    subowner_type = BramBlockStat
    subowner_identifier = "BRAM Statistics"


class BoardStat(StatAggregator):
    types_of_statistics = [
        IntradistanceStatistic,
        EntropyStatistic,
        InterdistanceStatistic,
    ]
    subowner_type = PBlockStat
    subowner_identifier = "PBlock Statistics"


class ExperimentStat(StatAggregator):
    types_of_statistics = [
        IntradistanceStatistic,
        EntropyStatistic,
        InterdistanceStatistic,
    ]
    subowner_type = BoardStat
    subowner_identifier = "Board Statistics"
