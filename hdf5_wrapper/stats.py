"""
Contains classes that inherit from SimpleStatistic, ComparisionStatistic or
BitwiseStatistic.
These are specialized Statistics for specific use cases
"""

from abc import abstractmethod
from pathlib import Path
from enum import Enum
from typing import Self, Type
import functools
import numpy as np
import numpy.typing as npt
import json
from .plotting import (
    stable_bit_per_read_step_plot,
    per_bit_idx_histogram,
    histogram,
    bit_heatmaps,
    multi_bit_heatmap,
    single_value_to_file,
    bytes_to_file,
    object_to_json_file
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
    reliability,
    stable_bits_per_idxs,
    interdistance,
)
from .utility import BitFlipType, ColorPresets, PlotSettings


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
        if 0 in self.data_percentage_count_dict:
            return self.data_percentage_count_dict[0]
        else:
            return 0

    @functools.cached_property
    def data_one_stable_bit_count(self) -> int:
        if 1.0 in self.data_percentage_count_dict:
            return self.data_percentage_count_dict[1.0]
        else:
            return 0

    @functools.cached_property
    def data_total_stable_bit_count(self) -> int:
        return self.data_zero_stable_bit_count + self.data_one_stable_bit_count

    @functools.cached_property
    def parity_zero_stable_bit_count(self) -> int:
        if 0 in self.parity_percentage_count_dict:
            return self.parity_percentage_count_dict[0]
        else:
            return 0

    @functools.cached_property
    def parity_one_stable_bit_count(self) -> int:
        if 1.0 in self.parity_percentage_count_dict:
            return self.parity_percentage_count_dict[1.0]
        else:
            return 0

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

        # self.flip_chance_to_1_per_bit_idx_plot(self.data_stats, "data")
        # self.flip_chance_to_1_per_bit_idx_plot(self.parity_stats, "parity")

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
    total_stable_bit_count = None
    stat_func_kwargs = {
        "bit_flip_type": BitFlipType.BOTH,
    }

    # Counts how many brams are included in this entity (1 one for single bram)
    bram_count = 1

    # Bit indices of a specific feature (e.g indices of random or stable bits)
    data_bit_indices = None
    # Data sample from all brams are later concatenated and used for NIST tests
    # To answer questions like: How is the quality of random bits?
    data_sample = None

    def __init__(
        self,
        plot_settings,
        read_session=None,
        data_read_stat=None,
        parity_read_stat=None,
        data_stable_bit_count=None,
        parity_stable_bit_count=None,
        bram_count: int = 1,
        data_sample: npt.NDArray[np.int8] = None
    ):
        super().__init__(
            plot_settings, read_session, data_read_stat, parity_read_stat
        )
        self.bram_count = bram_count
        self.data_bit_indices = [
            idx for idx, value in enumerate(self.data_stats)
            if value == self.bram_count
        ]
        if data_sample is None:
            if self.bram_count != 1:
                raise Exception(
                    "Either bram count is 1 and data_sample is None, or" \
                    "data_sample was provided and bram_count > 1." \
                    "A mixture of both cases implies and error."
                )
            else:
                self.data_sample = np.array([
                    read_session.data_reads[0].bits[int(idx/8)][idx%8]
                    for idx in self.data_bit_indices
                ])
        else:
            self.data_sample = data_sample


        if read_session is not None:
            self.data_stable_bit_count = sum(self.data_stats)
            self.parity_stable_bit_count = sum(self.parity_stats)

        else:
            self.data_stable_bit_count = data_stable_bit_count
            self.parity_stable_bit_count = parity_stable_bit_count
        

    def _plot(self) -> None:
        super()._plot()
        '''
        bit_heatmaps(
            self.data_stats,
            self.parity_stats,
            self.plot_settings.heatmap_bit_display_setting,
            "Number of Stable Bits per Bit Index",
            self.plot_settings.path,
            cmap=self.plot_settings.heatmap_cmap,
        )
        '''
        for bit_type, bit_stats in [
            ("data", self.data_stats),
            ("parity", self.parity_stats),
        ]:
            
            histogram(
                bit_stats,
                xlabel="TODO",
                ylabel="TODO",
                title="Distribution of Counts of Stable Bits per Bit Index",
                path=Path(
                    self.plot_settings.path,
                    f"{bit_type}_stable_bit_idx_count_distribution",
                ),
                bins=self.plot_settings.bram_count,
                log=False,
            )
            '''
            per_bit_idx_histogram(
                bit_stats,
                xlabel="TODO",
                ylabel="TODO",
                title="Distribution of stable bits per bit idx",
                path=Path(
                    self.plot_settings.path,
                    f"{bit_type}_stable_bit_idx_distribution",
                ),
            )
            '''

        single_value_to_file(self.data_stable_bit_count,
                    path=self.plot_settings.path,description="data_stable_bit_count")
        single_value_to_file(self.parity_stable_bit_count,
                    path=self.plot_settings.path, description="parity_stable_bit_count")

        if len(self.data_sample) > 0:
            data_sample_bytes = np.packbits(self.data_sample).tobytes()
        else:
            data_sample_bytes = b""
        bytes_to_file(data_sample_bytes,
                    path=self.plot_settings.path, description="data_sample")
        object_to_json_file(self.data_bit_indices,
                    path=self.plot_settings.path, description="idx.json")

        

    @classmethod
    def from_merge(
        cls, stats: list[Self], plot_settings: PlotSettings
    ) -> Self:
        """
        This merge is similar to BitwiseStatistic.from_merge,
        the main difference being that the values are not normalized by the
        number of samples.
        -> Because we want to get a distribution from total counts
        """
        data_read_stats_list = [
            bitwise_statistic.data_stats for bitwise_statistic in stats
        ]
        parity_read_stats_list = [
            bitwise_statistic.parity_stats for bitwise_statistic in stats
        ]

        data_read_stats_sum = np.array(
            list(map(sum, zip(*data_read_stats_list)))
        )
        parity_read_stats_sum = np.array(
            list(map(sum, zip(*parity_read_stats_list)))
        )
        data_stable_bit_count = sum([stat.data_stable_bit_count for stat in stats])/len(stats)
        parity_stable_bit_count = sum([stat.parity_stable_bit_count for stat in stats])/len(stats)
        bram_count = sum([stat.bram_count for stat in stats])
        data_samples = [stat.data_sample for stat in stats]

        merged_data_sample = np.concatenate(data_samples, axis=None)


        return cls(
            plot_settings, None, data_read_stats_sum, parity_read_stats_sum,
            data_stable_bit_count = data_stable_bit_count,
            parity_stable_bit_count = parity_stable_bit_count,
            bram_count = bram_count,
            data_sample = merged_data_sample
        )


class OneStableBitStatistic(StableBitStatistic):
    """
    Attributes:
        See parent classes
    """

    _hdf5_group_name = "One-stable Bits"
    description = "TODO"
    stat_func_kwargs = {"bit_flip_type": BitFlipType.ONE}
    plot_setting_additions = {
        "heatmap_cmap": ColorPresets.one_flipping_bit,
        "title": "X := One Stable Bits",
    }


class ZeroStableBitStatistic(StableBitStatistic):
    """
    Attributes:
        See parent classes
    """

    _hdf5_group_name = "Zero-stable Bits"
    description = "TODO"
    stat_func_kwargs = {"bit_flip_type": BitFlipType.ZERO}
    plot_setting_additions = {
        "heatmap_cmap": ColorPresets.zero_flipping_bit,
        "title": "X := Zero Stable Bits",
    }


class UnstableBitStatistic(StableBitStatistic):
    """
    Attributes:
        See parent classes
    """

    _hdf5_group_name = "Unstable Bits"
    description = "TODO"
    stat_func_kwargs = {"bit_flip_type": BitFlipType.UNSTABLE}
    plot_setting_additions = {
        "heatmap_cmap": ColorPresets.default,
        "title": "X := Unstable Bits (0.0 < p < 1.0)",
    }


class VeryUnstableBitStatistic(StableBitStatistic):
    """
    Attributes:
        See parent classes
    """

    _hdf5_group_name = "Very Unstable Bits"
    description = "TODO"
    stat_func_kwargs = {"bit_flip_type": BitFlipType.VERY_UNSTABLE}
    plot_setting_additions = {
        "heatmap_cmap": ColorPresets.default,
        "title": "X := Very Unstable Bits (0.25 <= p < 0.75)",
    }

class RandomBitStatistic(StableBitStatistic):
    """
    Attributes:
        See parent classes
    """

    _hdf5_group_name = "Random Bits"
    description = "TODO"
    stat_func_kwargs = {"bit_flip_type": BitFlipType.RANDOM}
    plot_setting_additions = {
        "heatmap_cmap": ColorPresets.default,
        "title": "X := Random Bits (0.4 <= p < 0.6)",
    }


class CombinedStableBitStatistic(BitwiseStatistic):
    """
    Attributes:
        See parent classes
    """

    _hdf5_group_name = "Combined Stable Bit Statistic"
    description = "TODO"
    stat_func = staticmethod(lambda x: x[0].bits_flattened)
    stat_func_kwargs = {}
    plot_setting_additions = {}
    stable_bit_stat_types: list[Type[StableBitStatistic]] = [
        # StableBitStatistic,
        ZeroStableBitStatistic,
        OneStableBitStatistic,
        UnstableBitStatistic,
        VeryUnstableBitStatistic,
    ]
    stable_bit_stats: dict[Type[StableBitStatistic], StableBitStatistic]

    def __init__(
        self,
        plot_settings,
        read_session=None,
        data_read_stat=None,
        parity_read_stat=None,
    ):
        super().__init__(
            plot_settings, read_session, data_read_stat, parity_read_stat
        )
        if read_session is not None:
            self.stable_bit_stats = {
                stable_bit_stat_type: stable_bit_stat_type(
                    plot_settings=plot_settings, read_session=read_session
                )
                for stable_bit_stat_type in self.stable_bit_stat_types
            }

    @classmethod
    def from_merge(
        cls, stats: list[Self], plot_settings: PlotSettings
    ) -> Self:
        new_stable_bit_stats = {
            stable_bit_stat_type: stable_bit_stat_type.from_merge(
                [
                    stat.stable_bit_stats[stable_bit_stat_type]
                    for stat in stats
                ],
                plot_settings.with_expanded_path(""),
            )
            for stable_bit_stat_type in cls.stable_bit_stat_types
        }
        new_stat_obj = cls(
            plot_settings,
            read_session=None,
            data_read_stat=np.zeros(4096 * 8),
            parity_read_stat=np.zeros(4096),
        )
        new_stat_obj.stable_bit_stats = new_stable_bit_stats
        return new_stat_obj

    def _plot(self):
        multi_bit_heatmap(
            self.stable_bit_stats,
            self.plot_settings.path,
            bram_count=self.plot_settings.bram_count,
            entity_name=self.plot_settings.entity_name,
        )


class UniformityStatistic(SingleValueStatistic):
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
    stat_func_kwargs = {"only_use_first_element": False}

    def plot(self) -> None:
        super().plot()
        bit_heatmaps(
            self.data_stats,
            self.parity_stats,
            self.plot_settings.heatmap_bit_display_setting,
            "Bit-aliasing per Bit Index",
            self.plot_settings.path,
        )


class ReliabilityStatistic(SingleValueStatistic):
    """
    Attributes:
        See parent classes
    """

    _hdf5_group_name = "Reliability"
    description = "TODO"
    stat_func = staticmethod(reliability)
    stat_func_kwargs = {}


class UniquenessStatistic(ComparisonStatistic):
    """
    Attributes:
        See parent classes
    """

    _hdf5_group_name = "Uniqueness"
    description = "TODO"
    stat_func = staticmethod(interdistance)
    stat_func_kwargs = {"only_use_first_element": True}


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
    UniformityStatistic = UniformityStatistic
    StableBitStatistic = StableBitStatistic
    ZeroStableBitStatistic = ZeroStableBitStatistic
    OneStableBitStatistic = OneStableBitStatistic
    UnstableBitStatistic = UnstableBitStatistic
    VeryUnstableBitStatistic = VeryUnstableBitStatistic
    RandomBitStatistic = RandomBitStatistic
    ReliabilityStatistic = ReliabilityStatistic
    UniquenessStatistic = UniquenessStatistic
    CombinedStableBitStatistic = CombinedStableBitStatistic
