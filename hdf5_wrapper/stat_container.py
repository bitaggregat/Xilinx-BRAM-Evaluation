"""
Module contains Statistic container objects.
These classes encapsulate iterations and handling of Statistic objects.
"""

from abc import ABCMeta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Self, Type
import h5py
from .experiment_hdf5 import ExperimentContainer, Experiment
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
    BitAliasingStatistic,
    BitFlipChanceStatistic,
    UniformityStatistic,
    StableBitStatistic,
    ZeroStableBitStatistic,
    OneStableBitStatistic,
    UnstableBitStatistic,
    VeryUnstableBitStatistic,
    RandomBitStatistic,
    ReliabilityStatistic,
    UniquenessStatistic,
    CombinedStableBitStatistic
)
from .utility import PlotSettings
from .plotting import multi_bit_heatmap, multi_bit_heatmap2 


@dataclass
class MultiReadSessionMetaStatistic(HDF5Convertible, Plottable):
    """
    Gathers MetaStatistic's of different ReadSessions
    Main objective:
    -> encapsulating the unification of MetaStatistic's
       and their handling in hdf5

    Attributes:
        data_meta_statistics: MetaStatistic objects of data bits, mapped by
                                read sesssion name
        parity_meta_statistics: Metastatistic objects of parity bits, mapped
                                by read session name
        _read_session_names: List of existing read session names/keys
        _hdf5_group_name: See HDF5Convertible
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
        """
        Creates latex table gives overview of meta stats created by this class

        Arguments:
            meta_stats_per_read_session: MetaStatistic objects ordered by there
                                            read session names.
            path: Path where diagram will be saved (file ext not included)
        """
        header = " & " + " & ".join(
            [
                "\\textbf{" + stat_name.replace("_", "\\_") + "}"
                for stat_name in MetaStatistic.statistic_method_names
            ]
        )
        table_format = "l" + "".join(
            ["c"] * len(MetaStatistic.statistic_method_names)
        )

        rows = [
            " & ".join(
                [read_session_name.replace("_", "\\_")]
                + [
                    str(meta_stat.stats[stat_name])
                    for stat_name in MetaStatistic.statistic_method_names
                ]
            )
            + "\\\\\n"
            for read_session_name, meta_stat
            in meta_stats_per_read_session.items()
        ]
        with open(path.with_suffix(".tex"), mode="w") as f:
            f.writelines(
                [
                    "\\begin{tabular}{|" + table_format + "|}\n",
                    header + "\\\\\n",
                    "\\toprule\n",
                ]
                + rows
                + ["\\bottomrule\n", "\\end{tabular}\n"]
            )

    def _plot(self) -> None:
        for bit_meta_stat, bit_type in [
            (self.data_meta_statistics, "data"),
            (self.parity_meta_statistics, "parity"),
        ]:
            self.multi_meta_stat_latex_table(
                bit_meta_stat,
                Path(self.plot_settings.path, f"{bit_type}_meta_stats"),
            )


@dataclass
class MultiReadSessionStatistic(HDF5Convertible, Plottable):
    """
    Gathers Statistics of different ReadSessions but same "Statistic"-type
    - e.g. "IntraDistance"-objects of ReadSessions "previous_value_00"
      and "previous_value_ff"

    Attributes:
        statistics: Statistic objects mapped by read session name
        statisitic_type: Statistic type used by this class
        _read_session_names: Names/Keys of existing read sessions
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
            self.plot_settings.with_expanded_path("all_meta_stats"),
            data_meta_stats,
            parity_meta_stats,
            self._read_session_names,
        )

    @classmethod
    def from_merge(
        cls,
        multi_rs_statistics: list[Self],
        statistic_type: Type[Statistic],
        read_session_names: list[str],
        plot_settings: PlotSettings,
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
                ],
                plot_settings.with_expanded_path(read_session_name),
            )
            for read_session_name in read_session_names
        }
        return cls(
            plot_settings, statistics, statistic_type, read_session_names
        )

    def add_to_hdf5_group(self, parent: h5py.Group) -> None:
        multi_group = parent.create_group(self._hdf5_group_name)
        for read_session_name in self._read_session_names:
            read_session_group = multi_group.create_group(read_session_name)
            self.statistics[read_session_name].add_to_hdf5_group(
                read_session_group
            )
        self.meta_stats.add_to_hdf5_group(multi_group)

    def _plot(self) -> None:
        if self.statistic_type.meta_statable:
            self.meta_stats.plot()
        for statistic in self.statistics.values():
            statistic.plot()


class MultiStatisticOwner(HDF5Convertible, Plottable, metaclass=ABCMeta):
    """
    Class that manages MultReadSessionObjects of different Statistic types.
    This is the Statistic container equivalent of a BramBlock object.
    -> It manages Stats (but doesn't manage other Statistic container objects)

    Attributes:
        name: Name of ExperimentContainer that was used for this object/class
        _read_session_names: List of existing read session names/keys
        used_statistics: List of Statistic types that will be calculated and
                            potentially plotted by this MultiStatisticOwner
        allowed_statistics: List of Statistic types that may be added to
                            "used_statistics" by user
    """

    name: str
    _read_session_names: list[str] = None
    statistics: dict[Type[Statistic], MultiReadSessionStatistic]
    used_statistics: list[
        Type[Statistic]
    ]  # Needs to be set by child class statically
    allowed_statistics: list = None

    def __init__(
        self,
        experiment_container: ExperimentContainer,
        plot_settings: PlotSettings,
    ) -> None:
        super().__init__(plot_settings)
        self._read_session_names = experiment_container.read_session_names
        self.name = experiment_container.name
        self.plot_settings.bram_count = experiment_container.bram_count
        self.plot_settings.entity_name = experiment_container.name
        self.statistics = dict()
        self.compute_stats(experiment_container)

    def compute_stats(self, experiment_container: ExperimentContainer) -> None:
        for statistic_type in self.used_statistics:
            if issubclass(statistic_type, SimpleStatistic):
                statistics_per_read_session = dict()
                for read_session_name in self._read_session_names:
                    statistics_per_read_session[read_session_name] = (
                        statistic_type(
                            self.plot_settings.with_expanded_path(
                                statistic_type._hdf5_group_name
                            ).with_expanded_path(read_session_name),
                            experiment_container.read_sessions[
                                read_session_name
                            ],
                        )
                    )
                self.statistics[statistic_type] = MultiReadSessionStatistic(
                    plot_settings=self.plot_settings.with_expanded_path(
                        statistic_type._hdf5_group_name
                    ),
                    statistics=statistics_per_read_session,
                    statistic_type=statistic_type,
                    _read_session_names=self._read_session_names,
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

        for statistic_type in self.used_statistics:
            if (
                statistic_type in self.statistics
                and self.statistics[statistic_type]
            ):
                self.statistics[statistic_type].add_to_hdf5_group(
                    multi_stat_group
                )
            else:
                continue

        return multi_stat_group

    def _plot(self) -> None:
        for statistic in self.statistics.values():
            statistic.plot()


class StatAggregator(MultiStatisticOwner, metaclass=ABCMeta):
    """
    Class for objects that
    manage multiple MultiStatisticOwner's (called substats)
    Provides aggregation functions for substats.

    Is the Statistic equivalent of PBlock or
    Board objects of "experiment.hdf5.py".
    The main objective of these classes is to reduce repetitive code duplicates

    Attributes:
        subowners: List of subordinated MultiStatisticOwner's
        subowner_type: Type of "subowners"
        subowner_identifier: String used for path in hdf5 path of subowner
                                Will be extracted from subcontainer

    """

    subowners: list[MultiStatisticOwner] = None
    subowner_type: Type[MultiStatisticOwner]
    subowner_identifier: str

    def compute_stats(self, experiment_container: ExperimentContainer) -> None:
        self.subowners = [
            self.subowner_type(
                plot_settings=self.plot_settings.with_expanded_path(
                    subcontainer.name
                ),
                experiment_container=subcontainer,
            )
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
            for statistic_type in self.used_statistics:
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
                            substats,
                            statistic_type,
                            self.read_session_names,
                            self.plot_settings.with_expanded_path(
                                statistic_type._hdf5_group_name
                            ),
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
            # Gather read_sessions of same read_session_name
            # for each container
            read_session_lists = experiment_container.read_sessions_unmerged
            
            # This below is the old version where values would be 
            # compared between containers instead of among all 
            # BRAMs of current container 
            #{
            #    read_session_name: [
                    
                    
                    #subcontainer.read_sessions[read_session_name]
                    #for subcontainer
                    #in experiment_container.subcontainers.values()
            #    ]
            #    for read_session_name in self.read_session_names
            #}
            if any(
                [
                    len(read_session_list) <= 1
                    for read_session_list in read_session_lists.values()
                ]
            ):
                print(
                    "Couldn't compare data of different instances"
                    f" of {experiment_container.name} because only one "
                    "sample was present"
                )
                return
            else:
                for statistic_type in self.used_statistics:
                    if issubclass(statistic_type, ComparisonStatistic):
                        statistics = {
                            read_session_name: statistic_type(
                                read_session_lists[read_session_name],
                                self.plot_settings.with_expanded_path(
                                    statistic_type._hdf5_group_name
                                ).with_expanded_path(read_session_name),
                            )
                            for read_session_name in self._read_session_names
                        }

                        self.statistics[statistic_type] = (
                            MultiReadSessionStatistic(
                                plot_settings=(
                                    self.plot_settings.with_expanded_path(
                                        statistic_type._hdf5_group_name
                                    )
                                ),
                                statistics=statistics,
                                statistic_type=statistic_type,
                                _read_session_names=self._read_session_names,
                            )
                        )

    def add_to_hdf5_group(self, parent: h5py.Group) -> h5py.Group:
        multi_stat_group = super().add_to_hdf5_group(parent)
        subowner_group = multi_stat_group.create_group(
            self.subowner_identifier
        )
        for subowner in self.subowners:
            subowner.add_to_hdf5_group(subowner_group)

    def _plot(self) -> None:
        if len(self.subowners) > 1:
            for statistic in self.statistics.values():
                statistic.plot()
        for subowner in self.subowners:
            subowner.plot()



class BramBlockStat(MultiStatisticOwner):
    """
    Attributes:
        See parent classes
    """
    
    allowed_statistics = [
        IntradistanceStatistic,
        EntropyStatistic,
        BitStabilizationStatistic,
        BitAliasingStatistic,
        BitFlipChanceStatistic,
        UniformityStatistic,
        StableBitStatistic,
        ZeroStableBitStatistic,
        OneStableBitStatistic,
        UnstableBitStatistic,
        VeryUnstableBitStatistic,
        RandomBitStatistic,
        ReliabilityStatistic,
        CombinedStableBitStatistic
    ]


class PBlockStat(StatAggregator):
    """
    Attributes:
        See parent classes
    """

    allowed_statistics = [
        IntradistanceStatistic,
        EntropyStatistic,
        BitAliasingStatistic,
        InterdistanceStatistic,
        BitFlipChanceStatistic,
        UniformityStatistic,
        StableBitStatistic,
        ZeroStableBitStatistic,
        OneStableBitStatistic,
        UnstableBitStatistic,
        VeryUnstableBitStatistic,
        RandomBitStatistic,
        ReliabilityStatistic,
        UniquenessStatistic,
        CombinedStableBitStatistic
    ]
    subowner_type = BramBlockStat
    subowner_identifier = "BRAM Statistics"


class BoardStat(StatAggregator):
    """
    Attributes:
        See parent classes
    """

    allowed_statistics = [
        IntradistanceStatistic,
        EntropyStatistic,
        BitAliasingStatistic,
        InterdistanceStatistic,
        BitFlipChanceStatistic,
        UniformityStatistic,
        ReliabilityStatistic,
        UniquenessStatistic,
        CombinedStableBitStatistic,
        StableBitStatistic,
        ZeroStableBitStatistic,
        OneStableBitStatistic,
        UnstableBitStatistic,
        VeryUnstableBitStatistic,
        RandomBitStatistic
    ]
    subowner_type = PBlockStat
    subowner_identifier = "PBlock Statistics"


class ExperimentStat(StatAggregator):
    """
    Attributes:
        See parent classes
    """

    allowed_statistics = [
        IntradistanceStatistic,
        EntropyStatistic,
        BitAliasingStatistic,
        InterdistanceStatistic,
        BitFlipChanceStatistic,
        UniformityStatistic,
        ReliabilityStatistic,
        UniquenessStatistic,
        CombinedStableBitStatistic
    ]
    subowner_type = BoardStat
    subowner_identifier = "Board Statistics"

    def plot_bit_aliasing_heatmap_per_device(self) -> None:
        data = {
            subowner.name:
            list(subowner.statistics[BitAliasingStatistic].statistics.values())[0].data_stats
            for subowner in self.subowners
        }
        data = {
            "Small (xczu1eg)": data["te0802"],
            "Medium (xczu2cg)": data["read_bram_te0802_zu2cg"],
            "Large (xczu9eg)": data["zcu102_eva_kit"],
            "All devices": list(self.statistics[BitAliasingStatistic].statistics.values())[0].data_stats
        }
        multi_bit_heatmap(
            bit_stats=data,
            path=self.plot_settings.path,
        )

    def plot_bit_aliasing_heatmap_levelwise(self) -> None:
        board = "te0802"
        b = [
            subowner for subowner in
            self.subowners if subowner.name == board
        ][0]
        column = b.subowners[0]
        bram_block = column.subowners[9]

        data = {
            "Small Board (xczu1eg)": list(b.statistics[BitAliasingStatistic].statistics.values())[0].data_stats,
            "Single Column": list(column.statistics[BitAliasingStatistic].statistics.values())[0].data_stats,
            f"Single {bram_block.name}": list(bram_block.statistics[BitAliasingStatistic].statistics.values())[0].data_stats
        }
        multi_bit_heatmap2(
            bit_stats=data,
            path=self.plot_settings.path,
        )


    def _plot(self):
        super()._plot()
    #    self.plot_bit_aliasing_heatmap_levelwise()


class StatContainers(Enum):
    """
    Attributes:
        See parent classes
    """

    BramBlockStat = BramBlockStat
    PBlockStat = PBlockStat
    BoardStat = BoardStat
    ExperimentStat = ExperimentStat

