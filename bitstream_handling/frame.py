from collections import defaultdict
from dataclasses import dataclass, field
from typing import List

import numpy as np

# TODO implement this in cpython for more speed
from position import XC7BitPosition


def int_to_np_bool_array(word: int) -> np.ndarray:
	assert 0 <= word <= 0xffffffff
	values = np.array([word], dtype=np.uint32).astype(">u4")
	temp = np.unpackbits(values.view(np.uint8), bitorder='big')
	zeros = np.zeros(32 - temp.size)
	temp = np.concatenate((zeros, temp), axis=0)
	return (temp != 0)[::-1]


def formatted_np_uint_str(word: np.ndarray) -> str:
	powers = 1 << np.arange(word.size, dtype=np.uint32)
	w = np.sum(powers * word)
	return "0" * (10 - len(hex(w))) + hex(w)[2:]


@dataclass(slots=True)
class Frame:
	addr: int
	words: np.ndarray = field(default_factory=lambda: np.zeros(shape=(101, 32), dtype=np.bool_))

	def __post_init__(self):
		if self.words.size != 3232:
			raise ValueError("Frame cannot be initialised with a word count other than 101")

	def __eq__(self, other):
		if isinstance(other, Frame) and self.addr == other.addr and (self.words == other.words).all():
			return True
		else:
			return False

	def normalized_addr(self) -> str:
		hex_str = hex(self.addr)
		return hex_str[:2] + "0" * (10 - len(hex_str)) + hex_str[2:]

	def to_frm_format(self) -> str:
		# Returns a string form of this frame that can be used by
		# the xc7patch script from the prjxray repository
		frame_str = ",".join([formatted_np_uint_str(w) for w in self.words])
		return f"{hex(self.addr)} {frame_str}"

	def to_text(self) -> str:
		# Uses the same representation as bitread from prjxray
		header = f".frame {self.normalized_addr}\n"
		return header + "\n".join([
			f"{formatted_np_uint_str(w)} " if idx % 6 != 0
			else f"{formatted_np_uint_str(w)}\n"
			for idx, w in enumerate(self.words)
		])

	def to_bytes(self) -> bytes:
		ints = np.flip(self.words, 1)
		ints = np.packbits(ints, axis=-1).view(np.uint32)
		return ints.view(np.dtype('<u4').newbyteorder()).tobytes()

	@classmethod
	def from_bit_list(cls, bit_list: List[XC7BitPosition], addr: int) -> "Frame":
		frame = cls(addr)
		for bit in bit_list:
			frame.set_bit(bit, True)

		return frame

	def set_bit(self, bit: XC7BitPosition, value: bool = True) -> None:
		self.words[bit.word][bit.bit_idx] = value

	def to_bit_list(self) -> List[XC7BitPosition]:
		"""
		:return: Positions of bits that are set true in this frame
		"""
		return [
			XC7BitPosition(self.addr, word_idx, bit_idx)
			for word_idx, word in enumerate(self.words)
			for bit_idx, bit in enumerate(word) if bit
		]

	@classmethod
	def from_bytes(cls, frame_addr: int, words: bytes) -> "Frame":
		return cls(frame_addr, np.array(
			[int_to_np_bool_array(int.from_bytes(words[i: i + 4], "big")) for i in range(0, len(words), 4)]))

	def is_empty(self) -> bool:
		for word in self.words:
			for bit in word:
				if bit:
					return False
		return True

	def __lt__(self, other):
		return self.addr < other.addr

	# Very old attempt at creating an checksum (which is not implemented because it is optional)
	"""
	def ecc(self) -> int:
		# TODO correct this implementation or use different one, as the current one does work
		# Currently used 
		# https://ieeexplore.ieee.org/document/8541471
		# Other possible solutions are:
		# https://github.com/f4pga/prjxray/blob/master/lib/xilinx/xc7series/ecc.cc
		# https://github.com/f4pga/prjxray/pull/70

		word_eccs = []
		wannabe_idx = 25
		for i, w in enumerate(self.words):
			if wannabe_idx == 32 or wannabe_idx == 64:
				wannabe_idx += 1
			word_eccs.append(w.ecc_polynomial(wannabe_idx))
			wannabe_idx += 1
		ecc = reduce(ixor, word_eccs)

		return ecc

	def set_ecc(self, ecc: int = None) -> None:
		# reset ecc to zero
		self.words[50] = Word(self.words[50] & 0xFFFFE000)
		if ecc is not None:
			self.words[50] = Word(self.words[50] | ecc)
		return None

	def eqs_without_ecc(self, other):
		An alternative to __eq__.
		Ignores the ecc words as they are not relevant to the configuration memory itself
		if not isinstance(other, Frame):
			raise ValueError(f"Frame cannot be compared with {type(other)}")
		for index, w1, w2 in enumerate(zip(self.words, other.words)):
			if w1 != w2 and index != 50:
				return False
		return True
	"""


def frames_from_bits(bits: List[XC7BitPosition]) -> List[Frame]:
	grouped_bits = defaultdict(list)
	for bit in bits:
		grouped_bits[bit.frame_addr].append(bit)

	frames = [Frame.from_bit_list(bit_list, frame_addr) for frame_addr, bit_list in grouped_bits.items()]
	return frames
