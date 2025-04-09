import unittest
import tempfile
from pathlib import Path

from hdf5_wrapper.main import main

class TestCreateNistDataSet(unittest.TestCase):

    test_hdf5 = Path(
        "tests", 
        "test_data",
        "mock_experiment_stability.hdf5"
    )

    def extract_data_from(self, path: Path) -> bytes:
        with open(path, mode="rb") as f:
            data = f.read()
            return data
    
    def extract_ascii_data_from(self, path: Path) -> bytes:
        with open(path) as f:
            data = f.readlines()
            return "".join(data).strip()

    def test_main(self) -> None:
        """
        High level test
        Extracts random and stable bits from mock data.
        Verifies output.
        """

        temp_dir = Path(tempfile.TemporaryDirectory().name)
        temp_file = Path(tempfile.NamedTemporaryFile().name)

        arg_dict = {
            "read_hdf5": self.test_hdf5,
            "plot_path": temp_dir,
            "out_hdf5": temp_file,
            "interdistance_k": None,
            "intradistance_k": None,
            "seed": 1337133713371337,
            "select_stats": [
                "RandomBitStatistic",
                "OneStableBitStatistic",
                "ZeroStableBitStatistic",
                "StableBitStatistic"
            ],
            "heatmap_bit_display_setting": "BOTH",
            "do_stats_stripewise": False,
            "base_session_name": None,
        }

        main(arg_dict)

        zero_stable_bit_count = self.extract_ascii_data_from(
            Path(
                temp_dir, 
                "Experiment/te0802/pblock_1/Zero-stable Bits/some_read_session",
                "data_stable_bit_count.txt"
            )
        )
        self.assertEqual(float(zero_stable_bit_count), 4096)


        one_stable_bit_count = self.extract_ascii_data_from(
            Path(
                temp_dir, 
                "Experiment/te0802/pblock_1/One-stable Bits/some_read_session",
                "data_stable_bit_count.txt"
            )
        )
        self.assertEqual(float(one_stable_bit_count), 4096)


        stable_bit_count = self.extract_ascii_data_from(
            Path(
                temp_dir, 
                "Experiment/te0802/pblock_1/Stable Bits/some_read_session",
                "data_stable_bit_count.txt"
            )
        )
        self.assertEqual(float(stable_bit_count), 8192)


        random_bit_count = self.extract_ascii_data_from(
            Path(
                temp_dir, 
                "Experiment/te0802/pblock_1/Random Bits/some_read_session",
                "data_stable_bit_count.txt"
            )
        )
        self.assertEqual(float(random_bit_count), 8192)
        
        one_stable_data_sample = self.extract_data_from(
            Path(
                temp_dir, 
                "Experiment/te0802/pblock_1/One-stable Bits/some_read_session",
                "data_sample"
            )
        )
        
        self.assertEqual(len(one_stable_data_sample), 1024)
        self.assertNotIn(b"\x00", one_stable_data_sample)

        stable_data_sample = self.extract_data_from(
            Path(
                temp_dir, 
                "Experiment/te0802/pblock_1/Stable Bits/some_read_session",
                "data_sample"
            )
        )
        
        self.assertEqual(len(stable_data_sample), 2048)
        self.assertEqual(stable_data_sample.count(b"\xff"), 1024)
        self.assertEqual(stable_data_sample.count(b"\x00"), 1024)



