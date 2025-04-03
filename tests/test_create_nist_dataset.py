import unittest
import tempfile
from pathlib import Path

class TestCreateNistDataSet(unittest.TestCase):

    test_hdf5 = Path(
        "tests", 
        "test_data",
        "mock_experiment_2025-04-03 03:21:03.107811.hdf5"
    )

    def extract_dataset_from(path: Path) -> bytes:
        with open(path, mode="rb") as f:
            data = f.read()
            return data

    def test_created_data(self) -> None:
        # execute main

        temporary_file = Path(tempfile.NamedTemporaryFile().name)

        
