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
from hdf5_wrapper.utility import PlotSettings


def unpack_from_hdf5(path: Path) -> Experiment:
    """
    Opens hdf5 and converts it to Experiment hdf5 wrapper class
    """
    with h5py.File(path, "r") as f:
        experiment = Experiment.from_hdf5(f, f.attrs["commit"])

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
        "--out_hdf5", required=True, help="Path where result hdf5 shall be written"
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
        type=Path
    )

def generate_plot_settings(arg_dict: dict[str, Any]) -> PlotSettings:
    if arg_dict["plot_path"] is None:
        return PlotSettings(
            None,
            False
        )
    else:
        return PlotSettings(
            arg_dict["plot_path"],
            True
        )


def main(arg_dict: dict[str, Any]):

    if arg_dict["interdistance_k"] is not None:
        InterdistanceStatistic.stat_func_kwargs["k"] = arg_dict[
            "interdistance_k"
        ]
    if arg_dict["intradistance_k"] is not None:
        IntradistanceStatistic.stat_func_kwargs["k"] = arg_dict[
            "intradistance_k"
        ]

    plot_settings = generate_plot_settings(arg_dict)
    # Unpack from bram read hdf5
    experiment = unpack_from_hdf5(arg_dict["read_hdf5"])

    with h5py.File(arg_dict["out_hdf5"], "w") as hdf5_file:
        add_commit_to_hdf5_group(hdf5_file)
        hdf5_file.attrs["rng seed"] = arg_dict["seed"]
        random.seed(arg_dict["seed"])

        experiment_stats = ExperimentStat(experiment, plot_settings.with_expanded_path("Experiment"))
        # Start computing stats
        experiment_stats.add_to_hdf5_group(hdf5_file)
        experiment_stats.plot()
        print("remove")