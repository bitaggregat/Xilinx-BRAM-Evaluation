from dataclasses import dataclass
from functools import cached_property, lru_cache
from typing import Tuple, Sequence



@dataclass(frozen=True)
class XilinxCoord:
	x: int
	y: int

	@classmethod
	def from_tile_name(cls, name: str) -> "XilinxCoord":
		row_col_str = name.split("_")[-1]
		x, y = row_col_str.replace("X", "_").replace("Y", "_").split("_")[1:]
		return cls(int(x), int(y))

	@lru_cache(maxsize=None)
	def coord_str(self) -> str:
		return f"X{self.x}Y{self.y}"


@dataclass(frozen=True)
class RegionCoords:
	"""
	Container for EvoRegion coordinates
	Allows to contain ugly coordinate comparison code in one class
	"""
	x1: int
	y1: int
	x2: int
	y2: int

	def contains(self, x: int, y: int) -> bool:
		return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2

	def min_equals(self, x: int, y: int) -> bool:
		return self.x1 == x and self.y1 == y

	def max_equals(self, x: int, y: int) -> bool:
		return self.x2 == x and self.y2 == y


@dataclass(frozen=True)
class XilinxRegionCoords:
	"""
	Same as Region coords but it uses the Xilinx grid convention instead:
	- INT and CLB share same XilinxCoord, but they have a different "normal" Coord
	"""
	min: XilinxCoord
	max: XilinxCoord


@dataclass(frozen=True)
class SegBitPosition:
	frame_offset: int
	bit_idx: int

	def to_dict(self) -> dict:
		return {
			"frame_offset": self.frame_offset,
			"bit_idx": self.bit_idx
		}

	@classmethod
	def from_segbit_str(cls, segbit_str: str) -> "SegBitPosition":
		parts = segbit_str.split("_")

		offset_str = parts[0].strip("!").lstrip("0")
		frame_offset = int(offset_str) if offset_str != '' else 0

		bit_pos_str = parts[1].lstrip("0").strip()
		bit_in_word = int(bit_pos_str) if bit_pos_str != '' else 0

		return cls(frame_offset, bit_in_word)


@dataclass(frozen=True)
class XC7ElementPosition:
	x: int
	y: int
	offset: int
	base_addr: int

	@classmethod
	def from_tilegrid_subdict(cls, subdict: dict) -> "XC7ElementPosition":
		if "bits" not in subdict:
			raise Exception("Error Tile has no position data. Adapt investigate (and maybe adapt implementation)")
		return cls(
			int(subdict["grid_x"]),
			int(subdict["grid_y"]),
			int(subdict["bits"]["CLB_IO_CLK"]["offset"]),
			int(subdict["bits"]["CLB_IO_CLK"]["baseaddr"], 16)
		)

	def to_dict(self):
		return {
			"x": self.x,
			"y": self.y,
			"offset": self.offset,
			"base_addr": self.base_addr
		}


@dataclass(frozen=True, slots=True)
class XC7BitPosition:
	frame_addr: int
	word: int
	bit_idx: int


	def to_ints(self) -> Tuple[int, ...]:
		return self.frame_addr, self.word, self.bit_idx

	@classmethod
	def from_ints(cls, int_seq: Sequence[int]):
		return cls(*int_seq)

	@classmethod
	def from_bitread_str(cls, str_repr: str) -> "XC7BitPosition":
		parts = str_repr.split("_")
		return XC7BitPosition(frame_addr=int(parts[1], 16), word=int(parts[2]), bit_idx=int(parts[3]))

	@classmethod
	def from_other_classes(cls, segbit: SegBitPosition, element_pos: XC7ElementPosition) -> "XC7BitPosition":
		bit_idx = segbit.bit_idx % 32
		word = element_pos.offset + int(segbit.bit_idx / 32)
		return cls(
			frame_addr=element_pos.base_addr + segbit.frame_offset,
			word=word,
			bit_idx=bit_idx
		)

	def __lt__(self, other):
		return (self.frame_addr < other.frame_addr or (self.frame_addr == other.frame_addr and self.word < other.word)
				or (self.frame_addr == other.frame_addr and self.word == other.word and self.bit_idx < other.bit_idx))
