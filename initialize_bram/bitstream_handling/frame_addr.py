import json
from collections import namedtuple
from pathlib import Path
from typing import List, Union, Iterable


def recursive_sum(l: List[Union[list, int]]) -> int:
	total = 0
	for i in l:
		if isinstance(i, list):
			total += recursive_sum(i)
		else:
			total += i
	return total


class FrameAddressGenerator:
	finished: bool = False
	counts: List[List[List[List[int]]]]  # block type/is_bottom/row/column/minor
	current_block_type: int = 0
	currently_is_bottom: int = 0  # 0 or 1
	current_row: int = 0
	current_column: int = 0
	current_minor: int = 0
	total = None
	# 2 Padding frames are needed after a row increment, source:
	# https://github.com/f4pga/prjxray/blob/master/lib/include/prjxray/xilinx/configuration.h
	padding_frames_needed: bool = False

	def __init__(self, counts: List[List[List[List[int]]]]):
		self.counts = counts

	def reset(self) -> None:
		self.finished = False
		self.current_block_type = 0
		self.currently_is_bottom = 0
		self.current_row = 0
		self.current_column = 0
		self.current_minor = 0
		self.total = None
		self.padding_frames_needed = False

	def __iter__(self):
		return self

	def __next__(self) -> Union[int, None]:
		re = self.current_addr()

		self.increment()
		return re

	def current_addr(self) -> Union[int, None]:
		if self.finished:
			return None
		re = 0
		re += self.current_block_type << 23
		re += self.currently_is_bottom << 22
		re += self.current_row << 17
		re += self.current_column << 7
		re += self.current_minor

		return re

	def first_addr_of_current_column(self) -> Union[int, None]:
		if self.finished:
			return None
		re = 0
		re += self.current_block_type << 23
		re += self.currently_is_bottom << 22
		re += self.current_row << 17
		re += self.current_column << 7

		return re

	def last_addr_of_current_column(self) -> Union[int, None]:
		current_addr = self.current_addr()
		current_column = self.current_column
		last_addr = current_addr

		if self.finished:
			return None

		while current_column == self.current_column:
			last_addr = next(self)

		return last_addr

	def increment(self) -> None:
		self.padding_frames_needed = False
		# Increment Minor
		if (self.counts[self.current_block_type][self.currently_is_bottom][self.current_row][self.current_column] >
				self.current_minor):
			self.current_minor += 1
		else:
			self.current_minor = 0

			# Increment Column
			if len(self.counts[self.current_block_type][self.currently_is_bottom][
					   self.current_row]) - 1 > self.current_column:
				self.current_column += 1
			else:
				self.current_column = 0

				# Increment Row
				self.padding_frames_needed = True
				if len(self.counts[self.current_block_type][self.currently_is_bottom]) - 1 > self.current_row:
					self.current_row += 1
				else:
					self.current_row = 0

					# Swap to bottom rows
					if not self.currently_is_bottom:
						self.currently_is_bottom = 1
					else:
						self.currently_is_bottom = 0

						# Change Block Type
						if 1 > self.current_block_type:
							self.current_block_type += 1
						else:
							self.finished = True

	def set_start(self, start: int) -> None:
		block_type = start >> 23
		if not 3 > block_type >= 0:
			raise Exception(f"Block Type {block_type} not possible, invalid address")
		self.current_block_type = block_type

		is_bottom = (start >> 22) & 1
		if not 2 > is_bottom >= 0:
			raise Exception(f"Bottom/Top bool {is_bottom} not possible, invalid address")
		self.currently_is_bottom = is_bottom

		row = (start >> 17) & (2 ** 5 - 1)
		if not len(self.counts[self.current_block_type][self.currently_is_bottom]) > row >= 0:
			raise Exception(f"Row {row} not possible, invalid address")
		self.current_row = row

		column = (start >> 7) & (2 ** 10 - 1)
		if not len(self.counts[self.current_block_type][self.currently_is_bottom][self.current_row]) > column >= 0:
			raise Exception(f"Column {column} not possible, invalid address")
		self.current_column = column

		minor = start & (2 ** 7 - 1)
		if not self.counts[self.current_block_type][self.currently_is_bottom][self.current_row][
				   self.current_column] >= minor >= 0:
			raise Exception(f"Minor {minor} not possible, invalid address")
		self.current_minor = minor

		self.padding_frames_needed = False

	@classmethod
	def from_part_json_content(cls, part_json_content: str) -> "FrameAddressGenerator":
		'''
		For now this works for artix7 xc7a35tcsg324-1 but it could fail for other models
		TODO: fix the issue above (longterm)
		'''

		temp_dict = json.loads(part_json_content)

		top_clb_io_rows, top_bram_rows = cls._rows_from_subdict(temp_dict["global_clock_regions"]["top"]["rows"])
		bot_clb_io_rows, bot_bram_rows = cls._rows_from_subdict(temp_dict["global_clock_regions"]["bottom"]["rows"])

		counts = [[top_clb_io_rows, bot_clb_io_rows], [top_bram_rows, bot_bram_rows], []]

		addr_gen = FrameAddressGenerator(counts)
		addr_gen.total = recursive_sum(counts)

		return addr_gen

	@staticmethod
	def _rows_from_subdict(subdict: dict) -> (List[List[int]], List[List[int]]):
		bram_rows = []
		clb_io_rows = []

		for key, value in subdict.items():
			bram_rows.append(list())
			clb_io_rows.append(list())
			for inner_key, inner_value in subdict[key]["configuration_buses"]["BLOCK_RAM"][
				"configuration_columns"].items():
				bram_rows[int(key)].append(int(inner_value["frame_count"]) - 1)
			for inner_key, inner_value in subdict[key]["configuration_buses"]["CLB_IO_CLK"][
				"configuration_columns"].items():
				clb_io_rows[int(key)].append(int(inner_value["frame_count"]) - 1)

		return clb_io_rows, bram_rows


FrameRange = namedtuple("FrameRange", ["start", "stop"])


class EvoRegionAddrDomain:
	frame_ranges: List[FrameRange]

	def __init__(self, frame_ranges: List[FrameRange]):
		self.frame_ranges = frame_ranges

	# TODO merge this
	@classmethod
	def from_addr_list(cls, addrs: Iterable[int], part_json_content: str) -> "EvoRegionAddrDomain":

		frame_ranges = list()

		for addr in addrs:
			if any([fr.start <= addr <= fr.stop for fr in frame_ranges]):
				continue
			else:
				temp_addr_gen = FrameAddressGenerator.from_part_json_content(part_json_content)
				temp_addr_gen.set_start(addr)

				frame_ranges.append(FrameRange(
					temp_addr_gen.first_addr_of_current_column(),
					temp_addr_gen.last_addr_of_current_column())
				)
		return cls(frame_ranges)

	def relevant_addrs(self) -> List[List[int]]:
		re = list()

		for fr in self.frame_ranges:
			re.append([addr for addr in range(fr.start, fr.stop + 1)])

		return re

	def relevant_addrs_flat(self) -> List[int]:
		re = list()

		for fr in self.frame_ranges:
			for addr in range(fr.start, fr.stop + 1):
				re.append(addr)

		return re
