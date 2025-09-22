import unittest
import numpy as np
import numpy.testing as nptest
from hdf5_wrapper.stat_functions import (
    bit_stabilization_count_over_time,
    bit_flip_chance,
    stable_bits_per_idxs,
    hamming_weight,
    reliability,
    interdistance_bootstrap,
    intradistance_bootstrap,
)
from hdf5_wrapper.experiment_hdf5 import Read
from hdf5_wrapper.utility import BitFlipType

@unittest.skip("Test is currently outdated")
class TestStatFunctions(unittest.TestCase):
    reads_homogene_00 = [
        Read.from_raw(b"\x00\x00\x00", cache_raw_read=True),
        Read.from_raw(b"\x00\x00\x00", cache_raw_read=True),
    ]
    reads_homogene_ff = [
        Read.from_raw(b"\xff\xff\xff", cache_raw_read=True),
        Read.from_raw(b"\xff\xff\xff", cache_raw_read=True),
    ]
    reads_heterogene = [
        Read.from_raw(b"\xff\x00\xff", cache_raw_read=True),
        Read.from_raw(b"\x00\xff\x00", cache_raw_read=True),
    ]
    reads_heterogene_similar = [
        Read.from_raw(b"\xff\xff\xff", cache_raw_read=True),
        Read.from_raw(b"\xf0\x0f\xf0", cache_raw_read=True),
    ]

    def test_bit_stabilization_count_over_time(self) -> None:
        reads = [
            Read.from_raw(b"\xbe\xee", cache_raw_read=True),
            Read.from_raw(b"\xae\xef", cache_raw_read=True),
            Read.from_raw(b"\xbe\xfe", cache_raw_read=True),
            Read.from_raw(b"\xae\xef", cache_raw_read=True),
            Read.from_raw(b"\xbe\xfe", cache_raw_read=True),
            Read.from_raw(b"\xbe\xef", cache_raw_read=True),
            Read.from_raw(b"\xbe\xee", cache_raw_read=True),
            Read.from_raw(b"\xbe\xee", cache_raw_read=True),
            Read.from_raw(b"\xbe\xee", cache_raw_read=True),
            Read.from_raw(b"\xbe\xef", cache_raw_read=True),
        ]
        # Index of read from which bit became stable:
        #   0000|0000|0005|0009
        # "stabilized bits per index" if minimal duration is 5:
        expected_result = np.array([13, 0, 0, 0, 1, 1, 0, 0, 0, 0])
        result = bit_stabilization_count_over_time(
            reads, stable_after_n_reads=5
        )

        nptest.assert_array_equal(result, expected_result)

        expected_result = np.array([13, 0, 0, 0, 1, 1, 0, 0, 0, 1])
        result = bit_stabilization_count_over_time(
            reads, stable_after_n_reads=1
        )

        nptest.assert_array_equal(result, expected_result)

        expected_result = np.array([13, 0, 0, 0, 1, 1, 0, 0, 0, 1])
        result = bit_stabilization_count_over_time(
            reads, stable_after_n_reads=0
        )

        nptest.assert_array_equal(result, expected_result)

    def test_bit_flip_chance(self) -> None:
        test_reads = [Read.from_raw(b"\xf0", cache_raw_read=True)] * 5000 + [
            Read.from_raw(b"\xff", cache_raw_read=True)
        ] * 5000

        expected_result = np.array(
            [1.0, 1.0, 1.0, 1.0, 0.5, 0.5, 0.5, 0.5], dtype=np.float64
        )
        result = bit_flip_chance(test_reads)

        nptest.assert_array_equal(expected_result, result)

    def test_stable_bits_per_idxs(self) -> None:
        reads = [
            Read.from_raw(b"\xaa", cache_raw_read=True),
            Read.from_raw(b"\xaa", cache_raw_read=True),
            Read.from_raw(b"\xaa", cache_raw_read=True),
            Read.from_raw(b"\xaa", cache_raw_read=True),
            Read.from_raw(b"\xaa", cache_raw_read=True),
            Read.from_raw(b"\xaa", cache_raw_read=True),
            Read.from_raw(b"\xab", cache_raw_read=True),
            Read.from_raw(b"\xab", cache_raw_read=True),
            Read.from_raw(b"\xab", cache_raw_read=True),
            Read.from_raw(b"\xa8", cache_raw_read=True),
        ]
        stable_bits_both = stable_bits_per_idxs(
            reads, bit_flip_type=BitFlipType.BOTH
        )
        expected_bits_both = np.array([1, 1, 1, 1, 1, 1, 0, 0])
        nptest.assert_array_equal(stable_bits_both, expected_bits_both)

        stable_bits_zero = stable_bits_per_idxs(
            reads, bit_flip_type=BitFlipType.ZERO
        )
        expected_bits_zero = np.array([0, 1, 0, 1, 0, 1, 0, 0])
        nptest.assert_array_equal(stable_bits_zero, expected_bits_zero)

        stable_bits_one = stable_bits_per_idxs(
            reads, bit_flip_type=BitFlipType.ONE
        )
        expected_bits_one = np.array([1, 0, 1, 0, 1, 0, 0, 0])
        nptest.assert_array_equal(stable_bits_one, expected_bits_one)

    def test_hamming_weight(self) -> None:
        reads = [
            Read.from_raw(b"\xaa", cache_raw_read=True),
            Read.from_raw(b"\x18", cache_raw_read=True),
            Read.from_raw(b"\x37", cache_raw_read=True),
            Read.from_raw(b"\xff", cache_raw_read=True),
            Read.from_raw(b"\x52", cache_raw_read=True),
            Read.from_raw(b"\x55", cache_raw_read=True),
            Read.from_raw(b"\x93", cache_raw_read=True),
            Read.from_raw(b"\xc4", cache_raw_read=True),
            Read.from_raw(b"\xfe", cache_raw_read=True),
            Read.from_raw(b"\xf3", cache_raw_read=True),
        ]
        expected = np.array(
            [0.5, 0.25, 5 / 8, 1, 3 / 8, 0.5, 0.5, 3 / 8, 7 / 8, 6 / 8]
        )
        nptest.assert_array_equal(expected, hamming_weight(reads))

        nptest.assert_array_equal(
            expected[:1], hamming_weight(reads, only_use_first_element=True)
        )

    def test_reliability(self) -> None:
        reads_1 = [
            Read.from_raw(b"\xaa", cache_raw_read=True),
            Read.from_raw(b"\x18", cache_raw_read=True),
            Read.from_raw(b"\x37", cache_raw_read=True),
            Read.from_raw(b"\xff", cache_raw_read=True),
            Read.from_raw(b"\x52", cache_raw_read=True),
            Read.from_raw(b"\x55", cache_raw_read=True),
            Read.from_raw(b"\x93", cache_raw_read=True),
            Read.from_raw(b"\xc4", cache_raw_read=True),
            Read.from_raw(b"\xfe", cache_raw_read=True),
            Read.from_raw(b"\xf3", cache_raw_read=True),
        ]
        expected_1 = (
            1
            - sum([4 / 8, 7 / 8, 4 / 8, 3 / 8, 1, 4 / 8, 4 / 8, 4 / 8, 4 / 8])
            / 9
        )
        self.assertEqual(expected_1, reliability(reads_1))

        reads_2 = [
            Read.from_raw(b"\xaa", cache_raw_read=True),
            Read.from_raw(b"\xaa", cache_raw_read=True),
            Read.from_raw(b"\xaa", cache_raw_read=True),
            Read.from_raw(b"\xaa", cache_raw_read=True),
            Read.from_raw(b"\xaa", cache_raw_read=True),
            Read.from_raw(b"\xaa", cache_raw_read=True),
            Read.from_raw(b"\xab", cache_raw_read=True),
            Read.from_raw(b"\xab", cache_raw_read=True),
            Read.from_raw(b"\xab", cache_raw_read=True),
            Read.from_raw(b"\xa8", cache_raw_read=True),
        ]
        expected_2 = 1 - sum([0, 0, 0, 0, 0, 1 / 8, 1 / 8, 1 / 8, 1 / 8]) / 9
        self.assertEqual(expected_2, reliability(reads_2))

    def test_intradistance_bootstrap(self) -> None:
        nptest.assert_array_equal(
            intradistance_bootstrap(self.reads_homogene_00), np.array([0])
        )

        nptest.assert_array_equal(
            intradistance_bootstrap(self.reads_heterogene), np.array([1.0])
        )
        nptest.assert_array_equal(
            intradistance_bootstrap(self.reads_heterogene_similar),
            np.array([0.5]),
        )

    def test_interdistance_bootstrap(self) -> None:
        nptest.assert_array_equal(
            interdistance_bootstrap(
                self.reads_homogene_00, self.reads_homogene_ff, k=2
            ),
            np.array([1, 1]),
        )

        nptest.assert_array_equal(
            interdistance_bootstrap(
                self.reads_homogene_00, self.reads_homogene_00, k=2
            ),
            np.array([0, 0]),
        )

        self.assertIn(
            list(
                interdistance_bootstrap(
                    self.reads_heterogene_similar, self.reads_homogene_00, k=2
                )
            ),
            [[0, 0.5], [0.5, 0], [0.5, 0.5], [0, 0]],
        )
        self.assertIn(
            list(
                interdistance_bootstrap(
                    self.reads_heterogene_similar, self.reads_heterogene, k=2
                )
            ),
            [[2 / 3, 0.5], [0.5, 2 / 3], [0.5, 0.5], [2 / 3, 2 / 3]],
        )
