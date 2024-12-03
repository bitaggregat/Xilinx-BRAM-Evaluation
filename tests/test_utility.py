import unittest
import numpy as np
import numpy.testing as nptest
from hdf5_wrapper.utility import combine_data_and_parity_bits

class TestUtility(unittest.TestCase):

    def test_combine_data_and_parity_bits(self) -> None:
        data_bits = np.ones((512 * 64,))
        parity_bits = np.zeros((64**2,))

        single_row = np.append(np.ones((64, ), np.zeros(8,)))
        expected_layered = np.fromiter((single_row for _ in range(512)), np.float64)
        expected = expected_layered.flatten()
        result = combine_data_and_parity_bits(data_bits, parity_bits)
        nptest.assert_array_equal(expected, result)
        self.assertEqual(len(result), 512 * 72)
