import unittest
from hdf5_wrapper.stats import intradistance_bootstrap, interdistance_bootstrap
from hdf5_wrapper.experiment_hdf5 import Read

class TestStats(unittest.TestCase):

    reads_homogene_00 = [
        Read(b'\x00\x00\x00'),
        Read(b'\x00\x00\x00'),
    ]
    reads_homogene_ff = [
        Read(b'\xff\xff\xff'),
        Read(b'\xff\xff\xff')
    ]
    reads_heterogene = [
        Read(b'\xff\x00\xff'),
        Read(b'\x00\xff\x00')
    ]
    reads_heterogene_similar = [
        Read(b'\xff\xff\xff'),
        Read(b'\xf0\x0f\xf0')
    ]

    def test_intradistance_bootstrap(self) -> None:
        
        self.assertEqual(
            intradistance_bootstrap(self.reads_homogene_00),
            [0, 0]
        )
        self.assertEqual(
            intradistance_bootstrap(self.reads_heterogene),
            [1, 1]
        )
        self.assertEqual(
            intradistance_bootstrap(self.reads_heterogene_similar),
            [0.5, 0.5]
        )
    
    def test_interdistance_bootstrap(self) -> None:
        self.assertEqual(
            interdistance_bootstrap(
                self.reads_homogene_00,
                self.reads_homogene_ff,
                k=2
            ),
            [1,1]
        )

        self.assertEqual(
            interdistance_bootstrap(
                self.reads_homogene_00,
                self.reads_homogene_00,
                k=2
            ),
            [0,0]
        )

        self.assertIn(
            interdistance_bootstrap(
                self.reads_heterogene_similar,
                self.reads_homogene_00,
                k=2
            ),
            [[0,0.5], [0.5,0], [0.5, 0.5], [0, 0]]
        )
        self.assertIn(
            interdistance_bootstrap(
                self.reads_heterogene_similar,
                self.reads_heterogene,
                k=2
            ),
            [[2/3, 0.5],[0.5, 2/3],[0.5, 0.5], [2/3, 2/3]]
        )