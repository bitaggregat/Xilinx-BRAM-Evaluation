


import unittest
from interlace_data_and_parity_bits import merge_data_sets

class TestMergeDataSets(unittest.TestCase):

    def test_merge_data_sets(self):

        test_pairs = [
            (
                b'\xff' * 8,
                b'\x00',
                False,
                b'\xff\x7f\xbf\xdf\xef\xf7\xfb\xfd\xfe'
            ),
            (
                b'\x00' * 8,
                b'\xff',
                False,
                b'\x00\x80\x40\x20\x10\x08\x04\x02\x01'
            ),
            (
                b'\xf0' * 8,
                b'\xf0',
                False,
                b'\xf0\xf8\x7c\x3e\x1f\x07\x83\xc1\xe0'
            ),
            (
                b'\xf0' * 8,
                b'\xf0',
                True,
                b'\xf0\x78\x3c\x1e\x0f\x0f\x87\xc3\xe1'
            )
        ]
        for data_bytes, parity_bytes, invert, expected_result in test_pairs:
            result = merge_data_sets(data_bytes, parity_bytes, invert)
            self.assertEqual(
                result, 
                expected_result
            )
            

    