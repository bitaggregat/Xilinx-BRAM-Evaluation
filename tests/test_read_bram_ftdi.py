import unittest
import reading.read_bram_ftdi as read_bram_ftdi
import os
import subprocess
import io
import sys
import tempfile

from pathlib import Path

vivado_path = Path("/tools/Xilinx/Vivado/2024.1/bin/vivado")

@unittest.skip("Test is currently outdated")
@unittest.skipIf(
    not os.path.isfile(vivado_path),
    reason="Skipped because vivado binary was not found. "
    "Change 'vivado_path' according to your systems configuration."
)
class TestReadBramFTDI(unittest.TestCase):
	
    read_bram_2e6_baud_bs = Path("tests", "test_data", "read_bram_2e6_baud.bit")
    flash_script = Path("tests", "test_data", "flash_bs.tcl")
    flashing_interface = 'localhost:3121/xilinx_tcf/Digilent/25163300869FA'
    uart_adapter_sn = "A801TJLF"

    def setUp(self) -> None:
        pass

        
    def flash_bs(self, bs_path: Path) -> None:
        """
        Flashes bitstream to device
        """
        subprocess.Popen(
            [
                vivado_path, 
                "-mode",
                "batch", 
                "-source",
                self.flash_script,
                "-tclargs", 
                self.flashing_interface,
                bs_path.resolve()
            ]
        )



    def test_failure_at_2e6_baud(self) -> None:
        """
        Test if measurment failure is caught
        """

        # Flash 2e6 bs (This bitstream is known to pose problems)
        self.flash_bs(self.read_bram_2e6_baud_bs)

        # Reroute console output
        captured_output = io.StringIO()
        sys.stdout = captured_output

        temporary_file = tempfile.NamedTemporaryFile()
        # Construct args for main method of script
        args = {
            "show_device": False,
            "failure_limit": 10,
            "device": self.uart_adapter_sn,
            "ftdi_interface": 1,
            "baudrate": 2e6,
            "output_path": temporary_file.name
        }

        for _ in range(10):
            read_bram_ftdi.main(args)
        
        self.assertIn("UART failure: stopping batch", captured_output.getvalue())

        # Set allowed failure limit to 0
        # Readout will now crash after one failure
        args["failure_limit"] = 0

        try:
            for _ in range(10):
                read_bram_ftdi.main(args)
        except Exception:
            self.assertIn("UART failed too many times. Aborting readout", captured_output.getvalue())
            sys.stdout = sys.__stdout__ # Reset redirect