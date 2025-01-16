import unittest
import numpy as np
import numpy.testing as nptest
import h5py
from pathlib import Path
from hdf5_wrapper import Experiment
from hdf5_wrapper.experiment_hdf5 import Read


class TestExperiment(unittest.TestCase):
    """
    Light sample test on Experiment hdf5 classes.
    """

    test_hdf5_file_path = Path(
        "tests", "test_data", "mock_experiment_2024-11-13.hdf5"
    )

    def test_init(self):
        # Load Experiment class from test data
        with h5py.File(self.test_hdf5_file_path, "r") as f:
            experiment = Experiment.from_hdf5(f, "commit_place_holder")

            bram_block_1 = (
                experiment.subcontainers["te0802"]
                .subcontainers["pblock_1"]
                .subcontainers["RAMB36_X2Y12"]
            )
            bram_block_2 = (
                experiment.subcontainers["te0802"]
                .subcontainers["pblock_1"]
                .subcontainers["RAMB36_X2Y13"]
            )

            self.assertEqual(len(bram_block_1.read_sessions), 1)
            # This is repetition of the same code block and could be refactored
            # But it shall suffice for testing (due to time management)
            self.assertEqual(
                len(
                    bram_block_1.read_sessions[
                        "previous_value_00_t=0"
                    ].data_reads
                ),
                len(
                    bram_block_2.read_sessions[
                        "previous_value_00_t=0"
                    ].data_reads
                ),
            )
            self.assertEqual(
                len(
                    bram_block_1.read_sessions[
                        "previous_value_00_t=0"
                    ].data_reads
                ),
                11,
            )
            self.assertEqual(
                len(
                    bram_block_1.read_sessions[
                        "previous_value_00_t=0"
                    ].parity_reads
                ),
                len(
                    bram_block_2.read_sessions[
                        "previous_value_00_t=0"
                    ].parity_reads
                ),
            )
            self.assertEqual(
                len(
                    bram_block_2.read_sessions[
                        "previous_value_00_t=0"
                    ].parity_reads
                ),
                11,
            )

            for read in bram_block_1.read_sessions[
                "previous_value_00_t=0"
            ].data_reads:
                self.assertEqual(len(read.raw_read), 4096)
                self.assertEqual(len(read.bits), 4096)
                for byte in read.bits:
                    self.assertEqual(len(byte), 8)

            for read in bram_block_2.read_sessions[
                "previous_value_00_t=0"
            ].parity_reads:
                self.assertEqual(len(read.raw_read), 512)
                self.assertEqual(len(read.bits), 512)
                for byte in read.bits:
                    self.assertEqual(len(byte), 8)


class TestRead(unittest.TestCase):
    reads_homogene_00 = [
        Read.from_raw(b"\x00\x00\x00"),
        Read.from_raw(b"\x00\x00\x00"),
    ]
    reads_homogene_ff = [
        Read.from_raw(b"\xff\xff\xff"),
        Read.from_raw(b"\xff\xff\xff"),
    ]
    reads_heterogene = [
        Read.from_raw(b"\xff\x00\xff"),
        Read.from_raw(b"\x00\xff\x00"),
    ]
    reads_heterogene_similar = [
        Read.from_raw(b"\xff\xff\xff"),
        Read.from_raw(b"\xf0\x0f\xf0"),
    ]

    def test_bits_flattened(self) -> None:
        for read, np_array in [
            (Read.from_raw(b"\x00\x00\x00"), np.zeros((24,))),
            (Read.from_raw(b"\xff\xff\xff"), np.ones((24,))),
            (
                Read.from_raw(b"\xf0\x0f\xf0"),
                np.array(
                    [
                        1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0,
                        1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0
                    ]
                ),
            ),
        ]:
            nptest.assert_array_equal(read.bits_flattened, np_array)

    def test_entropy(self) -> None:
        self.assertEqual(
            [read.entropy for read in self.reads_homogene_00], [0, 0]
        )
        self.assertEqual(
            [read.entropy for read in self.reads_homogene_ff], [0, 0]
        )
        self.assertEqual(
            [read.entropy for read in self.reads_heterogene_similar], [0, 1]
        )
        self.assertEqual(
            [read.entropy for read in self.reads_heterogene],
            [0.9182958340544894, 0.9182958340544894],
        )
