import unittest
from pathlib import Path

import fix_18k_read

class TestFix18KRead(unittest.TestCase):

    def test_fix_read(self) -> None:

        unfixed_read_path = Path("tests", "test_data", "unfixed_18k_read")
        # load read from file:
        with open(unfixed_read_path, mode="rb") as f:
            unfixed_read = f.read()

        fixed_read = fix_18k_read.fix_read(unfixed_read)

        self.assertTrue(
            fixed_read.count(b"\x00") < len(unfixed_read) / 4
        )
