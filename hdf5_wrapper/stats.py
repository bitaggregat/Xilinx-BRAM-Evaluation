from pathlib import Path
from .plotting import stable_bit_per_read_step_plot
from .stats_base import SimpleStatistic, ComparisonStatistic
from .stat_functions import (
    interdistance,
    intradistance,
    interdistance_bootstrap,
    intradistance_bootstrap,
    entropy_list,
    bit_stabilization_count_over_time,
)


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
    stat_func_kwargs = {"k": 100}


class BitStabilizationStatistic(SimpleStatistic):
    _hdf5_group_name = "Bit Stabilization"
    description = "TODO"
    stat_func = staticmethod(bit_stabilization_count_over_time)
    stat_func_kwargs = {"stable_after_n_reads": 5}

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
