from pathlib import Path
from typing import Any
import argparse
import random
import h5py
from hdf5_wrapper import (
    Experiment,
    ExperimentStat,
    InterdistanceStatistic,
    IntradistanceStatistic,
    add_commit_to_hdf5_group,
)
from hdf5_wrapper.plotting import single_value_bar_plot
from hdf5_wrapper.utility import PlotSettings, HeatmapBitDisplaySetting
from hdf5_wrapper.stats import StatisticTypes
from hdf5_wrapper.stat_container import StatContainers
import matplotlib
import gc

matplotlib.use("agg")
import time


def unpack_from_hdf5(
    path: Path,
    filter_even_stripes: bool = False,
    filter_uneven_stripes: bool = False,
) -> Experiment:
    """
    Opens hdf5 and converts it to Experiment hdf5 wrapper class
    """
    with h5py.File(path, "r") as f:
        experiment = Experiment.from_hdf5(
            f,
            f.attrs["commit"],
            filter_even_stripes=filter_even_stripes,
            filter_uneven_stripes=filter_uneven_stripes,
        )

    return experiment


def create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        "Script that takes BRAM experiment hdf5 file, unpacks the latter and "
        "computes various stats over the data\n"
        "Generated stats are saved in another hdf5 file."
    )
    parser.add_argument(
        "--read_hdf5",
        required=True,
        help="Path to hdf5 file containing bram reads",
    )
    parser.add_argument(
        "--out_hdf5",
        required=True,
        help="Path where result hdf5 shall be written",
    )
    parser.add_argument(
        "--interdistance_k",
        required=False,
        help="Sets how many samples will be drawn for the bootstrapping "
        "for interdistances",
    )
    parser.add_argument(
        "--seed",
        required=False,
        help="Seed that is used to initialize pythons random module "
        "(for reproducibility)",
        type=int,
        default=1337133713371337,
    )
    parser.add_argument(
        "--intradistance_k",
        required=False,
        help="Sets how many samples will be drawn for the bootstrapping "
        "for intradistances",
    )
    parser.add_argument(
        "--plot_path",
        required=False,
        help="Sets path where plot images will be saved. "
        "Plots will NOT be generated if no path is given.",
        default=None,
        type=Path,
    )
    parser.add_argument(
        "--select_stats",
        required=False,
        help="Types of statistics that shall be calculated.\n"
        f"Possible stats are: {[t.name for t in StatisticTypes]}",
        nargs="*",
        default=[],
    )
    parser.add_argument(
        "--heatmap_bit_display_setting",
        required=False,
        help="Sets how data and parity bits are displayed in heatmap diagrams"
        "See HeatmapBitDisplaySetting class\n"
        f"Possible stats are: {[s.name for s in HeatmapBitDisplaySetting]}",
        default=HeatmapBitDisplaySetting.BOTH.name,
    )
    parser.add_argument(
        "--base_session_name",
        required=False,
        help="Name of read session that shall be used as anchor for reliability intercomparison."
        "Chosing a name will activate this statistic",
        default="",
    )
    parser.add_argument(
        "--do_stats_stripewise", required=False, help="TODO", default=False,
        action="store_true"
    )
    return parser


def generate_plot_settings(arg_dict: dict[str, Any]) -> PlotSettings:
    """
    Generates PlotSettings object from arg_dict

    Arguments:
        arg_dict: Argument dict gained from argparser
    """
    if arg_dict["plot_path"] is None:
        return PlotSettings(
            None,
            False,
            None,
        )
    else:
        heatmap_bit_display_setting = HeatmapBitDisplaySetting[
            arg_dict["heatmap_bit_display_setting"]
        ]
        return PlotSettings(
            arg_dict["plot_path"],
            True,
            heatmap_bit_display_setting=heatmap_bit_display_setting,
        )


def select_stats(arg_dict: dict[str, Any]) -> None:
    """
    Function takes argument dictionary from argparser and activates
    statistics that were selected by user through args.

    Each Class in "StatContainers" has a list of allowed Statistics and a list
    of used Statistics.
    Statistics types selected by user will be statically added to the
    list of "used_statistics" of a Container class if they are allowed
    for said Containers

    Arguments:
        arg_dict: Dictionary created by argparser
    """

    for stat_container in StatContainers:
        stat_container.value.used_statistics = list()
        for stat_type in arg_dict["select_stats"]:
            if stat_type in [st.name for st in StatisticTypes]:
                if (
                    StatisticTypes[stat_type].value
                    in stat_container.value.allowed_statistics
                ):
                    stat_container.value.used_statistics.append(
                        StatisticTypes[stat_type].value
                    )
                else:
                    continue
            else:
                raise Exception(
                    f"Stat type {stat_type} is not available.\n"
                    f"Available types are: {[t.name for t in StatisticTypes]}"
                )

    # The block below isn't really best practice and should instead be handled
    # by some kind of subparser group
    # Future TODO
    if arg_dict["interdistance_k"] is not None:
        InterdistanceStatistic.stat_func_kwargs["k"] = arg_dict[
            "interdistance_k"
        ]
    if arg_dict["intradistance_k"] is not None:
        IntradistanceStatistic.stat_func_kwargs["k"] = arg_dict[
            "intradistance_k"
        ]


def reliability_intercomparison(
    experiment: Experiment, base_session_name: str, path: Path, title: str
) -> None:
    pblock = list(
        list(experiment.subcontainers.values())[0].subcontainers.values()
    )[0]
    value_dict, bram_names = pblock.reliability_intercomparison(
        base_session_name
    )
    single_value_bar_plot(value_dict, bram_names, title, path)


def main(arg_dict: dict[str, Any]):
    plot_settings = generate_plot_settings(arg_dict)
    select_stats(arg_dict)
    # Unpack from bram read hdf5
    if arg_dict["do_stats_stripewise"]:
        for stripe_name in [
            "filter_uneven_stripes", "filter_even_stripes"
        ]:
            experiment = unpack_from_hdf5(arg_dict["read_hdf5"], **{stripe_name: True})

            with h5py.File(arg_dict["out_hdf5"], "w") as hdf5_file:
                add_commit_to_hdf5_group(hdf5_file)
                hdf5_file.attrs["rng seed"] = arg_dict["seed"]
                random.seed(arg_dict["seed"])

                experiment_stats = ExperimentStat(
                    experiment, plot_settings.with_expanded_path(f"Experiment_{stripe_name}")
                )
                # Start computing stats
                # experiment_stats.add_to_hdf5_group(hdf5_file)
            print("STARTING PLOTTING")
            time.sleep(20)
            experiment_stats.plot()
            print("Experiment Stats: Done")
            del experiment
            del experiment_stats
            gc.collect()

    else:
        experiment = unpack_from_hdf5(arg_dict["read_hdf5"])

        if arg_dict["base_session_name"]:
            reliability_intercomparison(
                experiment=experiment,
                base_session_name=arg_dict["base_session_name"],
                title="Comparison of Reliability under Different Environmental Conditions",
                path=Path(plot_settings.path, "reliability_intercomparison"),
            )

        with h5py.File(arg_dict["out_hdf5"], "w") as hdf5_file:
            add_commit_to_hdf5_group(hdf5_file)
            hdf5_file.attrs["rng seed"] = arg_dict["seed"]
            random.seed(arg_dict["seed"])

            experiment_stats = ExperimentStat(
                experiment, plot_settings.with_expanded_path("Experiment")
            )
            # Start computing stats
            # experiment_stats.add_to_hdf5_group(hdf5_file)
        print("STARTING PLOTTING")
        #time.sleep(20)
        experiment_stats.plot()
        print("Experiment Stats: Done")
