"""
Fasms are seen as Feature Model nodes of a feature tree (in this project)

"""
from abc import ABC
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Tuple, Union

from position import XC7BitPosition, SegBitPosition, XC7ElementPosition, XilinxCoord



@dataclass(frozen=True)
class FasmFeature(ABC):
	"""
	Abstract base for all feature classes
	"""
	name: str


@dataclass(frozen=True, unsafe_hash=True, order=True)
class FasmLeafFeature(FasmFeature):
	"""
	Leaves are nodes without children in the Feature tree
	Only leaves contain XC7BitPositions
	"""
	positions: Tuple[XC7BitPosition, ...]
	inverted: Dict[XC7BitPosition, bool] = field(
		hash=False)  # Contains for each XC7BitPosition whether they are inverted


@dataclass(frozen=True)
class TemplateFasmLeafFeature(FasmFeature):
	"""
	Temporary FasmLeafFeature Factory
	"""
	positions: Tuple[SegBitPosition, ...]
	inverted: Tuple[bool, ...]  # Contains for each XC7BitPosition whether they are inverted

	@classmethod
	def from_temp_str(cls, temp_str: str) -> "TemplateFasmLeafFeature":
		temp_split = temp_str.split(" ")
		name = temp_split[0]
		positions = list()
		inverted = list()

		for segbit_str in temp_split[1:]:
			if "!" in segbit_str:
				inverted.append(True)
				positions.append(SegBitPosition.from_segbit_str(segbit_str[1:]))
			else:
				inverted.append(False)
				positions.append(SegBitPosition.from_segbit_str(segbit_str))

		return cls(name, tuple(positions), tuple(inverted))

	def to_fasm_leaf_feature(self, element_position: XC7ElementPosition) -> FasmLeafFeature:
		bit_positions = [
			XC7BitPosition.from_other_classes(segbit, element_position)
			for segbit in self.positions
		]
		inverted = {bit: invert for bit, invert in zip(bit_positions, self.inverted)}

		return FasmLeafFeature(self.name, tuple(bit_positions), inverted)