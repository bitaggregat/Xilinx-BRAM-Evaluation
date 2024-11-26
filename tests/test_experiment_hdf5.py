import unittest
import h5py
from pathlib import Path
from hdf5_wrapper import Experiment

class TestExperiment(unittest.TestCase):
    '''
    Light sample test on Experiment hdf5 classes.
    '''
    test_hdf5_file_path = Path("tests", "test_data", "test.hdf5")

    def test_init(self):

        # Load Experiment class from test data
        with h5py.File(self.test_hdf5_file_path, "r") as f:
            experiment = Experiment.from_hdf5(f, "commit_place_holder")

            bram_block = experiment.boards["te0802"].pblocks["pblock_1"].bram_blocks["RAMB36_X2Y12"]
            
            self.assertEqual(len(bram_block.read_sessions), 2)
            # This is repetition of the same code block and could be refactored
            # But it shall suffice for testing (due to time management)
            self.assertEqual(
                len(bram_block.read_sessions["previous_value_00"].data_reads),
                len(bram_block.read_sessions["previous_value_ff"].data_reads)    
            )
            self.assertEqual(
                len(bram_block.read_sessions["previous_value_00"].data_reads),
                1000    
            )
            self.assertEqual(
                len(bram_block.read_sessions["previous_value_00"].parity_reads),
                len(bram_block.read_sessions["previous_value_ff"].parity_reads)    
            )
            self.assertEqual(
                len(bram_block.read_sessions["previous_value_00"].parity_reads),
                1000    
            )
            self.assertEqual(
                len(bram_block.read_sessions["previous_value_00"].temperatures),
                1000
            )

            for read in bram_block.read_sessions["previous_value_00"].data_reads:
                self.assertEqual(len(read.raw_read), 4096)
                self.assertEqual(len(read.bits), 4096)
                for byte in read.bits:
                    self.assertEqual(len(byte), 8)
            
            for read in bram_block.read_sessions["previous_value_ff"].parity_reads:
                self.assertEqual(len(read.raw_read), 512)
                self.assertEqual(len(read.bits), 512)
                for byte in read.bits:
                    self.assertEqual(len(byte), 8)
