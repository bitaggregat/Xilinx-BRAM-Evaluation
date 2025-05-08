import argparse
from pathlib import Path
import json

import h5py
import numpy as np

from hdf5_wrapper.experiment_hdf5 import Experiment
from hdf5_wrapper.stat_functions import reliability



def create_argparser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        "Takes multiple hdf5 files of bram read data." \
        "Uses one of them as reference file and " \
        "calculates reliability for the others.\n" \
        "Reliability is calculatd for each bram block that exists in both files"
    )

    parser.add_argument(
        "--reference_file",
        help="File whose bram values are taken as a reference for reliability",
        type=Path,
        required=True
    )
    parser.add_argument(
        "--target_file",
        help="File whose reliability shall shall be targeted",
        type=Path,
        required=True
    )
    parser.add_argument(
        "--read_session",
        help="Target read session used in both hdf5 files",
        default="previous_value_00_t=0"
    )
    parser.add_argument(
        "--label",
        help="Label used in result output json",
        required=True
    )
    parser.add_argument(
        "--out_path",
        help="Path where output json shall be saved",
        type=Path,
        required=True
    )

    return parser


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


def iter_and_calc_reliabilities(
    reference_experiment: Experiment,
    target_experiment: Experiment,
    read_session_name: str
) -> dict[str, np.float64]:
    
    result_dict = dict()

    for board_name in target_experiment.subcontainers:
        for pblock_name in target_experiment.subcontainers[board_name].subcontainers:
            for bram_name in target_experiment.subcontainers[board_name].subcontainers[pblock_name].subcontainers:

                reference_read = (
                    reference_experiment.
                    subcontainers[board_name].
                    subcontainers[pblock_name].
                    subcontainers[bram_name].
                    read_sessions[read_session_name].data_reads[-1]
                )

                target_bram = (
                    target_experiment.
                    subcontainers[board_name].
                    subcontainers[pblock_name].
                    subcontainers[bram_name]
                )

                target_reads = target_bram.read_sessions[read_session_name].data_reads
                reads = [reference_read] + target_reads[:-1]
                if reads[0] is not reference_read:
                    raise Exception("Not good")
                if len(reads) != 100:
                    raise Exception(f"Unexpected length: {len(reads)}, {board_name}/{pblock_name}/{bram_name}")

                reliability_value = reliability(reads)
                result_dict[target_bram.name] = reliability_value
    return result_dict



def main(arg_dict: dict) -> None:

    reference_exp = unpack_from_hdf5(arg_dict["reference_file"])
    target_exp = unpack_from_hdf5(arg_dict["target_file"])

    result_dict =iter_and_calc_reliabilities(
        reference_experiment=reference_exp,
        target_experiment=target_exp,
        read_session_name=arg_dict["read_session"]
    )

    result_json = {
        "label": arg_dict["label"],
        "data": [value for value in result_dict.values()]
    }

    with open(arg_dict["out_path"], mode="w") as f:
        json.dump(result_json, f)


if __name__ == "__main__":

    parser = create_argparser()
    arg_dict = vars(parser.parse_args())

    main(arg_dict)