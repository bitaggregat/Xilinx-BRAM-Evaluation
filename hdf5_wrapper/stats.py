"""
Contains classes that inherit from SimpleStatisitc, ComparisionStatistic or
BitwiseStatistic.
These are specialized Statistics for specific use cases
"""

from abc import abstractmethod
from pathlib import Path
from enum import Enum
from typing import Self
import functools
import numpy as np
import numpy.typing as npt
from .plotting import (
    stable_bit_per_read_step_plot,
    per_bit_idx_histogram,
    histogram,
    bit_heatmaps,
)
from .stats_base import (
    SimpleStatistic,
    ComparisonStatistic,
    BitwiseStatistic,
    SingleValueStatistic,
)
from .stat_functions import (
    interdistance_bootstrap,
    intradistance_bootstrap,
    entropy_list,
    bit_stabilization_count_over_time,
    bit_flip_chance,
    hamming_weight,
    stable_bits_per_idxs,
)
from .utility import BitFlipType, ColorPresets


class IntradistanceStatistic(SimpleStatistic):
    """
    Attributes:
        See parent classes
    """

    _hdf5_group_name = "Intradistance"
    description = "Intradistance of Bootstrap of set of SUV's"
    "via relative Hamming Distance"
    stat_func = staticmethod(intradistance_bootstrap)
    stat_func_kwargs = {"k": 10000}


class EntropyStatistic(SimpleStatistic):
    """
    Attributes:
        See parent classes
    """

    _hdf5_group_name = "Entropy"
    description = "Entropy on single reads via counts of 1's and 0's in SUV"
    stat_func = staticmethod(entropy_list)


class InterdistanceStatistic(ComparisonStatistic):
    """
    Attributes:
        See parent classes
    """

    _hdf5_group_name = "Interdistance"
    description = "Interdistance values between Bootstrap of two sets of SUV's"
    stat_func = staticmethod(interdistance_bootstrap)
    stat_func_kwargs = {"k": 100000}


class BitStabilizationStatistic(SimpleStatistic):
    _hdf5_group_name = "Bit Stabilization"
    description = "Evolution of number of Stable Bits over time in Reads"
    stat_func = staticmethod(bit_stabilization_count_over_time)
    stat_func_kwargs = {"stable_after_n_reads": 1000}

    def _plot(self) -> None:
        super()._plot()

        stable_bit_per_read_step_plot(
            self.data_stats,
            "data",
            self.plot_settings.path,
            **self.stat_func_kwargs,
        )
        stable_bit_per_read_step_plot(
            self.parity_stats,
            "parity",
            self.plot_settings.path,
            **self.stat_func_kwargs,
        )


class BitFlipChanceStatistic(BitwiseStatistic):
    _hdf5_group_name = "Bitflip Percentage"
    description = "Percentage of times that SUV 1 occured per bit index. Also "
    "describes the number of Stable bits."
    stat_func = staticmethod(bit_flip_chance)
    stat_func_kwargs = {}

    # Alot of these count values will be used multiple times
    # Which is why we cache each of them as a class attribute
    @functools.cached_property
    def data_percentage_count_dict(self) -> dict:
        unique, counts = np.unique(self.data_stats, return_counts=True)
        return dict(zip(unique, counts))

    @functools.cached_property
    def parity_percentage_count_dict(self) -> dict:
        unique, counts = np.unique(self.parity_stats, return_counts=True)
        return dict(zip(unique, counts))

    @functools.cached_property
    def data_zero_stable_bit_count(self) -> int:
        return self.data_percentage_count_dict[0]

    @functools.cached_property
    def data_one_stable_bit_count(self) -> int:
        return self.data_percentage_count_dict[1.0]

    @functools.cached_property
    def data_total_stable_bit_count(self) -> int:
        return self.data_zero_stable_bit_count + self.data_one_stable_bit_count

    @functools.cached_property
    def parity_zero_stable_bit_count(self) -> int:
        return self.parity_percentage_count_dict[0]

    @functools.cached_property
    def parity_one_stable_bit_count(self) -> int:
        return self.parity_percentage_count_dict[1.0]

    @functools.cached_property
    def parity_total_stable_bit_count(self) -> int:
        return (
            self.parity_zero_stable_bit_count
            + self.parity_one_stable_bit_count
        )

    def create_flip_latex_table(self) -> None:
        """
        Gathers the number of stable bits (for 0 and 1) in a latex table.
        """
        header = [
            "Bit Type",
            "1-stable Bits total frequency",
            "1-stable Bits relative frequency",
            "0-stable Bits total frequency",
            "0-stable Bits relative frequency",
            "All stable Bits total frequency",
            "All stable Bits relative frequency",
        ]
        rows = [
            [
                "Data Bits",
                self.data_one_stable_bit_count,
                self.data_one_stable_bit_count / len(self.data_stats),
                self.data_zero_stable_bit_count,
                self.data_zero_stable_bit_count / len(self.data_stats),
                self.data_total_stable_bit_count,
                self.data_total_stable_bit_count / len(self.data_stats),
            ],
            [
                "Parity Bits",
                self.parity_one_stable_bit_count,
                self.parity_one_stable_bit_count / len(self.parity_stats),
                self.parity_zero_stable_bit_count,
                self.parity_zero_stable_bit_count / len(self.parity_stats),
                self.parity_total_stable_bit_count,
                self.parity_total_stable_bit_count / len(self.parity_stats),
            ],
        ]
        header_str = " & ".join(header) + "\\\\\n"
        rows_strs = [
            " & ".join([str(elem) for elem in row]) + "\\\\\n" for row in rows
        ]

        table_format = "|cclclcl|"

        with open(
            Path(self.plot_settings.path, "stable_bit_overview").with_suffix(
                ".tex"
            ),
            mode="w",
        ) as f:
            f.writelines(
                [
                    "\\begin{tabular}{" + table_format + "}\n",
                    header_str,
                    "\\hline\n",
                ]
                + rows_strs
                + ["\\end{tabular}\n"]
            )

    def flip_chance_to_1_per_bit_idx_plot(
        self, bit_stats: npt.NDArray[np.float64], bit_type: str
    ) -> None:
        """
        Wrapper around per_bit_idx_histogram where part of the description
        attributes is already set.

        Arguments:
            bits_stats: Numpy array of relative frequency of bitflip to 1
                        per bit idx
            bit_type: Either "Parity" or "Data". Will only be inserted into
                        description
        """

        per_bit_idx_histogram(
            bit_stats=bit_stats,
            xlabel="Bit indices",
            ylabel="Relative frequency of bit flipping to 1",
            title="Relative frequency of bit flip "
            f"per bit idx in {bit_type} bits",
            path=Path(
                self.plot_settings.path,
                f"{bit_type}_stable_bits_over_reads.svg",
            ),
        )

    def distribution_histogram(
        self, bit_stats: npt.NDArray[np.float64], bit_type: str
    ) -> None:
        """
        Wrapper around histogram function.
        Sets description attributes automatically.

        Attributes:
            bit_stats: Either self.parity_stats or self.data_stats
            bit_type: Either "parity" or "data". Will be inserted into
                        description
        """
        histogram(
            bit_stats=bit_stats,
            xlabel="Probabilty of bit flipping to 1",
            ylabel="Total frequency of probability",
            title="Distribution of probability of "
            "bit to flip to 1 of all bits",
            path=Path(
                self.plot_settings.path,
                f"bitflip_probability_distribution_of_{bit_type}_bits",
            ),
            bins=100,
        )

    def _plot(self) -> None:
        super()._plot()

        self.flip_chance_to_1_per_bit_idx_plot(self.data_stats, "data")
        self.flip_chance_to_1_per_bit_idx_plot(self.parity_stats, "parity")

        self.create_flip_latex_table()

        self.distribution_histogram(self.data_stats, "data")
        self.distribution_histogram(self.parity_stats, "parity")


class StableBitStatistic(BitwiseStatistic):
    """
    Attributes:
        See parent classes
    """

    _hdf5_group_name = "Stable Bits"
    description = "TODO"
    stat_func = staticmethod(stable_bits_per_idxs)
    stat_func_kwargs = {"bit_flip_type": BitFlipType.BOTH}

    def plot(self) -> None:
        super().plot()
        bit_heatmaps(
            self.data_stats,
            self.parity_stats,
            self.plot_settings.heatmap_bit_display_setting,
            "Number of Stable Bits per Bit Index",
            self.plot_settings.path,
            cmap=self.plot_settings.heatmap_cmap,
        )
        for bit_type, bit_stats in [
            ("data", self.data_stats),
            ("parity", self.parity_stats),
        ]:
            histogram(
                bit_stats,
                xlabel="TODO",
                ylabel="TODO",
                title="Distribution Stable Bits Bit Index",
                path=Path(
                    self.plot_settings.path,
                    f"{bit_type}_stable_bit_idx_distribution",
                ),
                bins="auto",
                log=True,
            )

    @classmethod
    @abstractmethod
    def from_merge(cls, stats: list[Self]) -> Self:
        """
        This merge as
        """
        data_read_stats_list = [
            bitwise_statistic.data_read_stat for bitwise_statistic in stats
        ]
        parity_read_stats_list = [
            bitwise_statistic.parity_read_stat for bitwise_statistic in stats
        ]

        data_read_stats_sum = list(map(sum, zip(*data_read_stats_list)))
        parity_read_stats_sum = list(map(sum, zip(*parity_read_stats_list)))

        return cls(None, data_read_stats_sum, parity_read_stats_sum)


class OneStableBitStatistic(StableBitStatistic):
    """
    Attributes:
        See parent classes
    """

    _hdf5_group_name = "One-stable Bits"
    description = "TODO"
    stat_func_kwargs = {"bit_flip_type": BitFlipType.ONE}
    plot_setting_additions = {"heatmap_cmap": ColorPresets.one_flipping_bit}


class ZeroStableBitStatistic(StableBitStatistic):
    """
    Attributes:
        See parent classes
    """

    _hdf5_group_name = "Zero-stable Bits"
    description = "TODO"
    stat_func_kwargs = {"bit_flip_type": BitFlipType.ZERO}
    plot_setting_additions = {"heatmap_cmap": ColorPresets.zero_flipping_bit}


class UniformityStatisitc(SingleValueStatistic):
    """
    Attributes:
        See parent classes
    """

    _hdf5_group_name = "Uniformity"
    description = "TODO"
    stat_func = staticmethod(hamming_weight)
    stat_func_kwargs = {"only_use_first_element": True}


class BitAliasingStatistic(BitwiseStatistic):
    """
    Attributes:
        See parent classes
    """

    _hdf5_group_name = "Bit-aliasing"
    description = "TODO"
    stat_func = staticmethod(bit_flip_chance)
    stat_func_kwargs = {"only_use_first_element": True}

    def plot(self) -> None:
        super().plot()
        bit_heatmaps(
            self.data_stats,
            self.parity_stats,
            self.plot_settings.heatmap_bit_display_setting,
            "Bit-aliasing per Bit Index",
            self.plot_settings.path,
        )


class StatisticTypes(Enum):
    """
    Lists all Statistics types that are selectable by user
    """

    IntradistanceStatistic = IntradistanceStatistic
    EntropyStatistic = EntropyStatistic
    InterdistanceStatistic = InterdistanceStatistic
    BitAliasingStatistic = BitAliasingStatistic
    BitStabilizationStatistic = BitStabilizationStatistic
    BitFlipChanceStatistic = BitFlipChanceStatistic
    UniformityStatisitc = UniformityStatisitc
    StableBitStatistic = StableBitStatistic
    ZeroStableBitStatistic = ZeroStableBitStatistic
    OneStableBitStatistic = OneStableBitStatistic
