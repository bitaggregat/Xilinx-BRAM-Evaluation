from pathlib import Path
import signal
import tempfile
import unittest
from hdf5_wrapper.main import main


def add_meta_stat_paths(
    base_path: Path, read_session_names: list[str], is_bram_dir: bool
) -> list[Path]:
    """
    Creates additional expected paths for meta statistics
    (Avoids code duplicates)

    Parameters:
        base_path: root path of newly created paths objects
        read_session_names: Names of read session of experiment
        is_bram_dir: bram directories are treated differently,
                        because they have no sub objects
    """
    if is_bram_dir:
        expanded_read_session_names = read_session_names
    else:
        expanded_read_session_names = read_session_names + ["all_meta_stats"]

    new_paths = list()
    for read_session_name in expanded_read_session_names:
        new_path = Path(base_path, read_session_name)
        new_paths.append(new_path)
        new_paths.append(Path(new_path, "parity_meta_stats.tex"))
        new_paths.append(Path(new_path, "data_meta_stats.tex"))
    return new_paths


def generate_expected_paths(
    base_path: Path, read_session_names: list[str]
) -> list[Path]:
    """
    Creates paths objects that are used to verify in test created directories

    Note: Not all created paths are tested. Only a handful of paths
            are tested (with good coverage)

    This method has repetitive elements, which shall suffice for now as it is
    only a test (also time management reasons)

    Parameters:
        base_path: root path of newly created paths objects
    """
    new_paths = list()
    current_path = Path(base_path)

    for next_subdirectory in [
        "Experiment",
        "te0802",
        "pblock_2",
        "RAMB36_X1Y12",
    ]:
        is_bram_dir = "RAMB" in next_subdirectory
        current_path = Path(current_path, next_subdirectory)
        new_paths.append(current_path)
        if is_bram_dir:
            bit_stabilization_path = Path(current_path, "Bit Stabilization")
            new_paths += add_meta_stat_paths(
                bit_stabilization_path,
                read_session_names,
                is_bram_dir=is_bram_dir,
            )
            for read_session_name in read_session_names:
                new_paths.append(
                    Path(
                        bit_stabilization_path,
                        read_session_name,
                        "data_stable_bits_over_reads.svg",
                    )
                )
                new_paths.append(
                    Path(
                        bit_stabilization_path,
                        read_session_name,
                        "parity_stable_bits_over_reads.svg",
                    )
                )
        for new_dir in ["Entropy", "Intradistance"]:
            temp_statistic_path = Path(current_path, new_dir)
            new_paths.append(temp_statistic_path)

            new_paths += add_meta_stat_paths(
                temp_statistic_path,
                read_session_names,
                is_bram_dir=is_bram_dir,
            )
    return new_paths


class TestPlotting(unittest.TestCase):
    plot_directory = tempfile.TemporaryDirectory()
    plot_path = plot_directory.name

    def setUp(self) -> None:
        """
        Prepare removal of tmp directory via signal,
        in case the program is interrupted (happens alot during debugging)
        """
        for sig in (
            signal.SIGABRT,
            signal.SIGILL,
            signal.SIGINT,
            signal.SIGSEGV,
            signal.SIGTERM,
        ):
            signal.signal(sig, self.tearDown)

    def tearDown(self) -> None:
        """
        Removes temporary directories created by tests.
        """
        self.plot_directory.cleanup()

    def test_main(self) -> None:
        """
        High level test
        Calls main and verifies if all expected images/latex files were created
        under the right path.
        TODO: Add new paths to this test whenever new plots are added.
        """
        arg_dict = {
            "read_hdf5": "tests/test_data/mock_experiment_2024-11-13.hdf5",
            "plot_path": self.plot_path,
            "out_hdf5": Path(self.plot_path, "hdf"),
            "interdistance_k": None,
            "intradistance_k": None,
            "seed": 1337133713371337,
            "select_stats": ["BitStabilizationStatistic", "IntradistanceStatistic", "EntropyStatistic"]
        }

        main(arg_dict)

        expected_paths = generate_expected_paths(
            self.plot_path, read_session_names=["previous_value_00_t=0"]
        )

        for path in expected_paths:
            self.assertTrue(path.exists())
