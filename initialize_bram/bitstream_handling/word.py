from dataclasses import dataclass
from functools import reduce
from operator import ixor
from typing import List


@dataclass
class Word:
	# array type is used here because it is more efficient and the number of bits is static
	bits: int = 0

	def __post_init__(self):
		if self.bits > 2 ** 32 - 1:
			raise ValueError(f"Value given for Word {self.bits} too big. Limit is 32 bits")

	def set_bit(self, value: bool, position: int) -> None:
		if not 0 <= position <= 31:
			raise ValueError(f"Position {position} is not viable for a 32 bit offset")
		if value:
			self.bits |= 1 << position
		else:
			self.bits &= ~(1 << position)

	def get_bit(self, position) -> bool:
		if not 0 <= position <= 31:
			raise ValueError(f"Position {position} is not viable for a 32 bit offset")
		return self.bits & (1 << position)

	def __int__(self):
		return self.bits

	def __hex__(self):
		return hex(self.bits)

	def __str__(self):
		# produces a string of length 8
		# fills the higher bits with zeros if the hexadecimal is too short
		hex = self.__hex__()
		# 10 because a hex string has +2 length
		# e.g. "0x6f708" has a length of 7 but only 5 digits
		return "0" * (10 - len(hex)) + hex[2:]

	def __eq__(self, other):
		if isinstance(other, Word):
			return other.bits == self.bits
		elif isinstance(other, int):
			return other == self.bits
		else:
			raise ValueError(f"Cannot compare {type(other)} and Word")

	def __and__(self, other):
		if isinstance(other, Word):
			return other.bits & self.bits
		elif isinstance(other, int):
			return other & self.bits
		else:
			raise ValueError(f"Cannot use bitwise & on  {type(other)} and Word")

	def __or__(self, other):
		if isinstance(other, Word):
			return other.bits | self.bits
		elif isinstance(other, int):
			return other | self.bits
		else:
			raise ValueError(f"Cannot use bitwise | on {type(other)} and Word")

	@classmethod
	def from_hex_str(cls, hex_str: str) -> "Word":
		if len(hex_str) == 8 or (len(hex_str) == 10 and hex_str[0:2] == "0x"):
			return cls(bits=int(hex_str, 16))
		else:
			raise ValueError(f"Wrong length {len(hex_str)}. A Word is 32 bits big")

	@classmethod
	def from_bytes(cls, byte_word: bytes) -> "Word":
		if len(byte_word) > 4:
			raise ValueError(f"Bytes given (byte_word) too long ({len(byte_word)}). Max size is 4")
		return cls(bits=int.from_bytes(byte_word, "big"))

	def to_bytes(self):
		return self.bits.to_bytes(4, "big")

	def true_idx(self) -> List[int]:
		"""
		:return: List indices of bits that are set to 1
		"""
		return [idx for idx in range(31) if self.get_bit(idx)]

	def xor_product(self, mask: List[int] = None) -> bool:
		if mask is not None:
			values = [bool(self.bits & (1 << i)) for i in mask]
		else:
			values = [bool(self.bits & (1 << i)) for i in range(32)]
		return reduce(ixor, values)
