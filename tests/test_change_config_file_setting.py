import unittest
from pathlib import Path
import tempfile
from change_config_file_setting import main

class TestChangeConfigFileSetting(unittest.TestCase):

    def test_main(self) -> None:
        
        temp_file = tempfile.NamedTemporaryFile().name

        arg_dicts = [
            {
                "config_file": Path("tests", "test_data", "input_config.sh"),
                "inplace": False,
                "output_file": Path(temp_file),
                "attribute": "output_path",
                "new_value": "/home/kiya/Repos/temp/xilinx-bram-evaluation/measurements/auto/new_measurements/measurement_with_specific_temperature"
            },
            {
                "config_file": Path(temp_file),
                "inplace": True,
                "output_file": None,
                "attribute": "reads",
                "new_value": 100
            },
            {
                "config_file": Path(temp_file),
                "inplace": True,
                "output_file": None,
                "attribute": "uart_sn",
                "new_value": "Peter"
            },
            {
                "config_file": Path(temp_file),
                "inplace": True,
                "output_file": None,
                "attribute": "use_previous_value_ff",
                "new_value": ""
            }
        ]

        for arg_dict in arg_dicts:
            main(**arg_dict)
        
        with open(Path(temp_file)) as f:
            result_lines = f.readlines()
        with open(Path("tests", "test_data", "expected_output_config.sh")) as f:
            expected_lines = f.readlines()

        print(expected_lines)
        print(result_lines)
        self.assertEqual(
            set(result_lines),
            set(expected_lines)
        )



