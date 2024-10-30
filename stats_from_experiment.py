from typing import Tuple, Dict, List
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from scipy.stats import chi2_contingency
from scipy.stats.contingency import odds_ratio
import argparse
import numpy as np
import h5py


from hdf5_wrapper import (
    Experiment,
    ExperimentStat,
    InterdistanceStatistic,
    IntradistanceStatistic,
)


def unpack_from_hdf5(path: Path) -> Experiment:
    """
    Opens hdf5 and converts it to Experiment hdf5 wrapper class
    """
    with h5py.File(path, "r") as f:
        experiment = Experiment.from_hdf5(f, f.attrs["commit"])

    return experiment


parser = argparse.ArgumentParser(
    "Script that takes BRAM experiment hdf5 file, unpacks the latter and does a chi squared test over the data\n"
    "The goal is to prove that certain variables do not influence bitflips in the bram"
)
parser.add_argument(
    "--read_hdf5", required=True, help="Path to hdf5 file containing bram reads"
)
parser.add_argument(
    "--out_hdf5", required=True, help="Path where result hdf5 shall be written"
)
parser.add_argument(
    "--interdistance_k",
    required=False,
    help="Sets how many samples will be drawn for the bootstrapping for interdistances",
)
parser.add_argument(
    "--intradistance_k",
    required=False,
    help="Sets how many samples will be drawn for the bootstrapping for intradistances",
)


def main():
    args = parser.parse_args()
    arg_dict = vars(args)

    if arg_dict["interdistance_k"] is not None:
        InterdistanceStatistic.stat_func_kwargs["k"] = arg_dict["interdistance_k"]
    if arg_dict["intradistance_k"] is not None:
        IntradistanceStatistic.stat_func_kwargs["k"] = arg_dict["intradistance_k"]

    experiment = unpack_from_hdf5(arg_dict["read_hdf5"])
    with h5py.File(arg_dict["out_hdf5"], "w") as hdf5_file:
        # TODO save read_session_names as attributes in experiment hdf5
        experiment_stats = ExperimentStat(experiment)
        experiment_stats.add_to_hdf5_group(hdf5_file)


if __name__ == "__main__":
    main()
