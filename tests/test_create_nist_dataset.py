import unittest
import tempfile
from pathlib import Path

import create_nist_dataset

@unittest.skip("Test is currently outdated")
class TestCreateNistDataSet(unittest.TestCase):

    test_hdf5 = Path(
        "tests", 
        "test_data",
        "mock_experiment_2025-04-03 03:21:03.107811.hdf5"
    )

    def extract_dataset_from(self, path: Path) -> bytes:
        with open(path, mode="rb") as f:
            data = f.read()
            return data
        
    def test_y_index_from_bram_name(self) -> None:
        bram_names = ["RAMB36_X2Y12", "RAMB36_X0Y0", "RAMB36_X2Y33"]
        expected_indices = [12, 0, 33]

        for name, index in zip(bram_names, expected_indices):
            self.assertEqual(
                create_nist_dataset.y_index_from_bram_name(name),
                index
            )

    def test_separate_stripes(self) -> None:
        data = (b"\xff" * 4 + b"\x00" * 8 + b"\xff" * 4) * 4 * 64
        expected_stripe_1 = b"\xff" * 2048
        expected_stripe_2 = b"\x00" * 2048

        stripe_1, stripe_2 = create_nist_dataset.separate_stripes(data)
        self.assertEqual(stripe_1, expected_stripe_1)
        self.assertEqual(stripe_2, expected_stripe_2) 

    def test_created_data(self) -> None:
        # execute main

        temporary_file = Path(tempfile.NamedTemporaryFile().name)

        expected_data_separate_stripes = (
            (b"\x00" * 2048 * 12 + b"\xff" * 2048 * 12)  * 9
        )

        expected_data_normal = (
            (b"\x00" * 4 + b"\xff" * 8 + b"\x00" * 4) * 4 * 64 * 12 * 9
        )

        args = {
            "input_hdf5": str(self.test_hdf5),
            "output_file": temporary_file,
            "setting": create_nist_dataset.DataSetting.PBLOCK_WISE,
            "groupe_pblocks_by": "None"
        }

        create_nist_dataset.main(args)
        
        self.assertEqual(
            self.extract_dataset_from(temporary_file),
            expected_data_normal
        )

        args["setting"] = create_nist_dataset.DataSetting.SEPARATE_STRIPES

        create_nist_dataset.main(args)

        self.assertEqual(
            self.extract_dataset_from(temporary_file),
            expected_data_separate_stripes
        )

        
