import subprocess
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional, List, Union, Set

from pyftdi.ftdi import Ftdi
from pyftdi.serialext import serial_for_url
from pyftdi.serialext.protocol_ftdi import Serial

from copenFPGALoader import CopenFPGALoaderConn


@dataclass(slots=True)
class InterfaceData:
	vid: int
	pid: int
	sn: str
	bus: int
	name: str


def get_available_ftdi(black_list: Optional[List[str]] = None) -> InterfaceData:
	# TODO more conditions and verifications for suitability?
	raw_list = [interface for interface in Ftdi.find_all([(0x0403, 0x6010)], True)]
	if black_list is None:
		black_list = []

	interface_tuples = {d for d, c in raw_list if d.sn not in black_list and d.description.startswith("Digilent")}

	if len(interface_tuples) == 0:
		return None

	choice = interface_tuples.pop()

	return InterfaceData(choice.vid, choice.pid, choice.sn, choice.bus, choice.description)


def xc7_device_unavailable() -> bool:
	return get_available_ftdi() is None


class FlashingMode(Enum):
	WRITE_THEN_SEND = auto()
	SEND_ONLY = auto()


def flash_bitstream_file_openFPGALoader(bitstream_path: str, sn: str) -> None:
	# TODO make this work with sn instead of board product name "basys3"
	args = ["openFPGALoader", "--board", "basys3", "--freq", str(30000000)]
	if sn is not None:
		args += ["--ftdi-serial", str(sn)]
	args.append(bitstream_path)
	try:
		output = subprocess.check_output(args)
	except subprocess.CalledProcessError as cpe:
		print(cpe.output)


@dataclass(slots=True)
class Basys3:
	"""
	Class that handles:
	- Flashing bitstreams onto xc7a35tcpg236-1 fpga of a basys3 board
	- Communicating via UART with said FPGA
	"""

	interface: InterfaceData
	mode: FlashingMode
	uart: Serial = field(init=False)
	conn: CopenFPGALoaderConn = None
	partial: bool = True
	registered_uuids: Set[uuid.UUID] = field(init=False, default_factory=set)

	def __post_init__(self):
		self.uart = serial_for_url(f"ftdi://::{self.interface.sn}/2", timeout=5)
		self.conn = CopenFPGALoaderConn()
		#self.conn.open(self.serial_number)

	def flash_bitstream_file_spi(self, bitstream_path: str) -> None:
		# TODO?
		pass

	@classmethod
	def from_available(cls, flashing_mode: FlashingMode = FlashingMode.WRITE_THEN_SEND, partial: bool = True) \
			-> "Basys3":
		"""
		Will look for a fitting basys3 board and instantiates object from its data
		"""
		interface_data = get_available_ftdi()
		if interface_data is None:
			raise Exception("No suitable devices found.")

		return cls(interface_data, flashing_mode, partial=partial)

	@property
	def serial_number(self) -> str:
		return self.interface.sn

	@property
	def hardware_type(self) -> str:
		return self.interface.name

	def flash_bs_file_copenFPGALoader(
			self, bitstream_path: Union[str, Path], board: str = "basys3", partial: bool = False) -> None:
		self.conn.flash_bitstream(False, partial, path=str(bitstream_path))

	def flash_bs_bytes_copenFPGALoader(self, bitstream_bytes: bytes, board: str = "basys3", partial: bool = False) -> None:
		self.conn.flash_bitstream(True, partial, bitstream_bytes=bitstream_bytes)


	def read_bytes(self, size: int) -> bytes:
		return self.uart.read(size)

	def write_bytes(self, data: bytes) -> int:
		return self.uart.write(data)

	def __enter__(self):
		self.conn.open(self.serial_number)
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.conn.close()
		self.uart.flush()
		self.uart.close()