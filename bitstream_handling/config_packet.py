from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from typing import List, Union

import numpy as np

from word import Word


class OPCode(Enum):
	NOP = 0
	READ = 1
	WRITE = 2


class PacketType(Enum):
	TYPE1 = 1
	TYPE2 = 2


class Register(Enum):
	CRC = 0
	FAR = 1
	FDRI = 2
	FDRO = 3
	CMD = 4
	CTL0 = 5
	MASK = 6
	STAT = 7
	LOUT = 8
	COR0 = 9
	MFWR = 10
	CBC = 11
	IDCODE = 12
	AXSS = 13
	COR1 = 14
	# Careful 15 is unknown
	WBSTAR = 16
	TIMER = 17
	# Careful 18 is unknown
	RBCRC_SW = 19
	BOOTSTS = 20
	# Careful 21, 22, 23 unknown
	CTL1 = 24
	# Careful many unknown addresses
	BSPI = 31


@dataclass(frozen=True)
class ConfigWord:
	packet_type: PacketType
	op_code: OPCode
	count: int
	register: Register = None

	def __post_init__(self):
		if self.packet_type == PacketType.TYPE2 and self.register is not None:
			raise ValueError(f"Type 2 packet don't use registers but Register \"{self.register}\" was given.")
		elif self.packet_type == PacketType.TYPE1 and self.register is None:
			raise ValueError(f"Type 1 packet use a target register but No register was given.")

	@cached_property
	def bits(self) -> np.uint32:
		bits = np.uint32(0)
		bits |= self.packet_type.value << 29
		bits |= self.op_code.value << 27
		if self.packet_type == PacketType.TYPE1:
			bits |= self.register.value << 13

			if self.count >= 2 ** 11:
				raise ValueError(f"Payload Word Count {self.count} is too big for Type 1 packet. Max size is {2 ** 11}")
		else:
			if self.count >= 2 ** 27:
				raise ValueError(f"Payload Word Count {self.count} is too big for Type 2 packet. Max size is {2 ** 27}")

		bits |= self.count
		return np.uint32(bits)

	def __hex__(self):
		return hex(self.bits)

	@classmethod
	def from_bytes(cls, byte_word: bytes) -> "ConfigWord":
		if len(byte_word) != 4:
			raise ValueError(f"Argument \"byte_word\" has wrong size. {len(byte_word)} but 4 expected")
		byte_word = int.from_bytes(byte_word, "big")

		packet_type = PacketType((byte_word >> 29) & 7)  # 111
		op_code = OPCode((byte_word >> 27) & 3)  # 11

		if packet_type == PacketType.TYPE1:
			count = byte_word & 4095  # (2 ** 12 - 1) (11 ones)
			register = Register((byte_word >> 13) & 31)  # 11111
		else:
			count = byte_word & 268435455  # (2 ** 28 - 1) (27 ones)
			register = None

		return cls(
			packet_type=packet_type,
			op_code=op_code,
			count=count,
			register=register
		)

	@cached_property
	def bytes(self) -> bytes:
		return self.bits.view(np.dtype('<u4').newbyteorder()).tobytes()

	def __repr__(self):
		if self.op_code != OPCode.NOP:
			return f"ConfigWord(packet_type={self.packet_type}, op_code={self.op_code}, register={self.register}, count={self.count})"
		else:
			return "ConfigWord(NOP)"

	def code_str(self) -> str:
		# This is currently used for testing only
		return str(hex(self.bits))


@dataclass(frozen=True)
class ConfigPacket:
	config_word: ConfigWord
	payload: Union[bytes, List[np.uint32]]

	def __post__init__(self):
		if isinstance(self.payload, bytes):
			length = len(self.payload) / 4
		else:
			length = len(self.payload)

		if length != self.config_word.count:
			raise ValueError(
				f"Wrong payload size. ConfigWord expects payload of {self.config_word.count} words, but {length} words were given.")

	@cached_property
	def payload_bytes(self) -> bytes:
		if isinstance(self.payload, bytes):
			return self.payload
		else:
			return b''.join([w.view(np.dtype('<u4').newbyteorder()).tobytes() for w in self.payload])

	@cached_property
	def bytes(self) -> bytes:
		return self.config_word.bytes + self.payload_bytes

	@cached_property
	def payload_words(self) -> List[Word]:
		if isinstance(self.payload, list):
			return self.payload
		else:
			return [Word.from_bytes(self.payload[i:i + 4]) for i in range(0, len(self.payload), 4)]

	def __str__(self):
		'''
		Expensiv please use this for debugging only
		'''
		return f"{self.config_word}: " + self.payload_bytes.hex()

	def __repr__(self):
		return self.__str__()

	def __eq__(self, other) -> bool:
		if isinstance(other, ConfigPacket) and \
				other.payload_bytes == self.payload_bytes and other.config_word == self.config_word:
			return True
		else:
			return False
