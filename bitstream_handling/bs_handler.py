from copy import deepcopy
from dataclasses import dataclass, field
from functools import reduce
from pathlib import Path
from typing import List, Dict, Union, Sequence

from frame import Frame, frames_from_bits
from frame_addr import FrameAddressGenerator, EvoRegionAddrDomain
from header import *
from position import XC7BitPosition

def remove_bram_init_packets(bs_bytes: bytes, bram_frame_batch_start_addr: str) -> bytes:
		
	synch_word_idx = bs_bytes.find(bytes.fromhex("AA995566"))
	header = bs_bytes[:synch_word_idx + 4]

	init_packets = list()
	temp_frames = list()
	suffix_packets = list()

	cfg_packet_gen = PacketGenerator(bs_bytes[synch_word_idx + 4:])

	cfg_packets = list()

	cfg_packet = next(cfg_packet_gen)

	while cfg_packet is not None:
		cfg_packets.append(cfg_packet)
		cfg_packet = next(cfg_packet_gen)

	skip = 0
	new_packets = list()

	hex_bram_frame_batch_start_addr = bytes.fromhex(bram_frame_batch_start_addr)
	for packet in cfg_packets:
		if packet.config_word.register == Register.FAR and packet.payload == hex_bram_frame_batch_start_addr:
			skip = 4
		if skip:
			skip -= 1
		else:
			new_packets.append(packet)

	new_bitstream = b''
	for packet in new_packets:
		new_bitstream += packet.bytes

	return sw_header(len(new_bitstream)) + new_bitstream


@dataclass(slots=True, init=True)
class XC7BSHandler:
	device_idcode: bytes
	partial_init_packets: List[ConfigPacket] = field(default_factory=list)
	partial_suffix_packets: List[ConfigPacket] = field(default_factory=list)
	full_init_packets: List[ConfigPacket] = field(default_factory=list)
	full_suffix_packets: List[ConfigPacket] = field(default_factory=list)
	frame_dict: Dict[int, Frame] = field(default_factory=dict)
	frames: List[Frame] = field(default_factory=list)
	habitat_frames: List[Frame] = field(default_factory=list)
	evo_frames: List[Frame] = field(default_factory=list)
	evo_frame_dict: Dict[int, Frame] = field(default_factory=dict)
	evolvable_region_packets: List[ConfigPacket] = field(default_factory=list)
	evo_is_setup: bool = False
	addr_gen: FrameAddressGenerator = None

	def __post_init__(self):

		self.partial_init_packets = partial_init_packets(self.device_idcode)
		self.partial_suffix_packets = partial_suffix_packets()
		self.full_init_packets = full_init_packets(False, self.device_idcode)
		self.full_suffix_packets = full_suffix_packets(False)

	def setup(self, part_json_content: str, evo_bits: Dict[XC7BitPosition, bool], habitat_bits: List[XC7BitPosition] = None) -> None:
		"""
		NOTE: Calling this will delete previous evo_frames, evo_frame_dict in order to prevent uncalled behaviour
		NOTE 2: evo_bits_dict values will overwrite habitat _evo_bits (if there is an overlap)
		"""
		self.addr_gen = FrameAddressGenerator.from_part_json_content(part_json_content)

		if habitat_bits is not None:
			self.frames = sorted(frames_from_bits(habitat_bits))
		self.habitat_frames = [deepcopy(frame) for frame in self.frames]

		temp_evo_frames = sorted(frames_from_bits(list(evo_bits.keys())))

		# Check overlap of habitat and evo_region
		previous_addrs = {f.addr for f in self.frames}
		evo_addrs = {f.addr for f in temp_evo_frames}
		addr_intersection = previous_addrs.intersection(evo_addrs)

		for ef in temp_evo_frames:
			if ef.addr in addr_intersection:
				# Update already existing Frame
				idx = [index for index, frame in enumerate(self.frames) if frame.addr == ef.addr][0]
				for bit in ef.to_bit_list():
					self.frames[idx].set_bit(bit)
			else:
				self.frames.append(ef)

		self.frames.sort()
		self.frame_dict = {frame.addr: frame for frame in self.frames}

		# Some Frames may be part of partial region despite not having any evolvable bits
		# This (below) finds them and adds them and previous evo_frames together
		evo_region = EvoRegionAddrDomain.from_addr_list(evo_addrs, part_json_content)
		evo_region_addrs = evo_region.relevant_addrs_flat()

		self.evo_frames = [frame for frame in self.frames if frame.addr in evo_region_addrs]
		self.evo_frame_dict = {f.addr: f for f in self.evo_frames}
		self.evo_is_setup = True

	def get_bit(self, bit: XC7BitPosition) -> bool:
		if bit.frame_addr in self.frame_dict:
			return bool(self.frame_dict[bit.frame_addr].words[bit.word][bit.bit_idx])
		else:
			raise KeyError(f"Bit {bit} is neither part of habitat nor of evo_region")

	def set_bit(self, bit: XC7BitPosition, value: bool) -> None:
		self.evo_frame_dict[bit.frame_addr].set_bit(bit, value)

	def set_multi_bits(self, bit_seq: Sequence[XC7BitPosition], value_seq: Sequence[bool]) -> None:
		for bit, val in zip(bit_seq, value_seq):
			self.evo_frame_dict[bit.frame_addr].set_bit(bit, val)

	def get_evo_frame_bits(self) -> List[XC7BitPosition]:
		"""
		bits in evo frames that are set true
		"""
		return [
			bit
			for frame in self.evo_frames
			for bit in frame.to_bit_list()
		]

	@classmethod
	def from_file(cls, bit_file: Path | str, part_json: Path | str) -> "XC7BSHandler":
		with open(bit_file, mode="rb") as f:
			return XC7BSHandler.from_bytes(f.read(), part_json)

	@classmethod
	def from_bytes(cls, bs_bytes: bytes, part_json: Union[Path, str]) -> "XC7BSHandler":
		
		synch_word_idx = bs_bytes.find(bytes.fromhex("AA995566"))
		header = bs_bytes[:synch_word_idx + 4]

		init_packets = list()
		temp_frames = list()
		suffix_packets = list()

		cfg_packet_gen = PacketGenerator(bs_bytes[synch_word_idx + 4:])

		cfg_packets = list()

		cfg_packet = next(cfg_packet_gen)

		while cfg_packet is not None:
			cfg_packets.append(cfg_packet)
			cfg_packet = next(cfg_packet_gen)

		with open(part_json) as f:
			content = "\n".join(f.readlines())
			addr_gen = FrameAddressGenerator.from_part_json_content(content)
			order_packets(cfg_packets, init_packets, temp_frames, suffix_packets, addr_gen)
			frames = list()
			for frame in temp_frames:
				if frame.is_empty():
					continue
				else:
					frames.append(frame)

			# Maybe put a part of this into constructor for minimal messiness
			bs = cls(grab_idcode_from_packets(init_packets))
			addr_gen.reset()
			bs.addr_gen = addr_gen
			bs.frames = frames
			return bs

	def bytes(self, partial: bool = False) -> bytes:
		if partial:
			return self.partial_evo_bytes()
		else:
			return self.full_bytes()

	def habitat_bs_bytes(self) -> bytes:
		self.addr_gen.reset()
		empty_frame_bytes = bytes.fromhex("00000000") * 101

		config_data = b''
		frame_idx = 0
		total = 0
		while not self.addr_gen.finished:
			addr = next(self.addr_gen)
			total += 1
			if frame_idx is not None and addr == self.habitat_frames[frame_idx].addr:
				config_data += self.habitat_frames[frame_idx].to_bytes()
				frame_idx += 1
				if frame_idx == len(self.habitat_frames):
					frame_idx = None
			else:
				config_data += empty_frame_bytes

			if self.addr_gen.padding_frames_needed:
				config_data += empty_frame_bytes * 2
				total += 2

		main_payload = [
			CommonPackets.set_far(0),
			CommonPackets.SET_CMD_1,
			ConfigPacket(CommonWords.NOP, b''),
			CommonPackets.FDRI_FULLW_PREP,
			ConfigPacket(CommonWords.write_type2(total * 101), config_data)
		]

		# Why not just use "sum()"? Because it doesn't work on bytes (very confusing).
		payload = reduce(
			lambda x, y: x + y,
			[packet.bytes for packet in self.full_init_packets + main_payload + self.full_suffix_packets]
		)
		return sw_header(len(payload)) + payload


	def full_bytes(self) -> bytes:
		self.addr_gen.reset()
		empty_frame_bytes = bytes.fromhex("00000000") * 101

		config_data = b''
		frame_idx = 0
		total = 0
		while not self.addr_gen.finished:
			addr = next(self.addr_gen)
			total += 1
			if frame_idx is not None and addr == self.frames[frame_idx].addr:
				config_data += self.frames[frame_idx].to_bytes()
				frame_idx += 1
				if frame_idx == len(self.frames):
					frame_idx = None
			else:
				config_data += empty_frame_bytes

			if self.addr_gen.padding_frames_needed:
				config_data += empty_frame_bytes * 2
				total += 2

		main_payload = [
			CommonPackets.set_far(0),
			CommonPackets.SET_CMD_1,
			ConfigPacket(CommonWords.NOP, b''),
			CommonPackets.FDRI_FULLW_PREP,
			ConfigPacket(CommonWords.write_type2(total * 101), config_data)
		]

		# Why not just use "sum()"? Because it doesn't work on bytes (very confusing).
		payload = reduce(
			lambda x, y: x + y,
			[packet.bytes for packet in self.full_init_packets + main_payload + self.full_suffix_packets]
		)
		return sw_header(len(payload)) + payload

	def partial_evo_bytes(self) -> bytes:
		if not self.evo_frames:
			raise Exception(
				"Can't generate bitstream bytes of evolvable region because no evolvable region was defined previously."
				"Did you setup the BitstreamHandler or this Bitstream object as intended?")

		main_payload = list()

		self.addr_gen.reset()

		# NOTE: Currently only one continuous (one "block") evolvable region is supported.
		# TODO Add option to do multiple writes (would be useful if evo region is actually 2 separate regions)
		self.addr_gen.set_start(self.evo_frames[0].addr)
		min_clb_addr = self.addr_gen.first_addr_of_current_column()
		self.addr_gen.set_start(self.evo_frames[-1].addr)
		max_clb_addr = self.addr_gen.last_addr_of_current_column()
		self.addr_gen.set_start(min_clb_addr)
		total = 0
		config_data = b''
		empty_frame_bytes = bytes.fromhex("00000000") * 101

		current_addr = next(self.addr_gen)
		while current_addr <= max_clb_addr:
			if current_addr in self.evo_frame_dict:
				config_data += self.evo_frame_dict[current_addr].to_bytes()
			else:
				config_data += empty_frame_bytes
			total += 1

			if self.addr_gen.padding_frames_needed:
				config_data += empty_frame_bytes * 2
				total += 2

			current_addr = next(self.addr_gen)
		# For some unknown reason an extra empty frame is needed here
		config_data += empty_frame_bytes
		total += 1

		main_payload.append(CommonPackets.set_far(min_clb_addr))
		main_payload.append(CommonPackets.SET_CMD_1)
		main_payload.append(ConfigPacket(CommonWords.NOP, b''))
		main_payload.append(CommonPackets.FDRI_FULLW_PREP)
		main_payload.append(ConfigPacket(CommonWords.write_type2(total * 101), config_data))

		payload = reduce(
			lambda x, y: x + y,
			[packet.bytes for packet in self.partial_init_packets + main_payload + self.partial_suffix_packets]
		)
		return sw_header(len(payload)) + payload


def grab_idcode_from_packets(cfg_packets: List[ConfigPacket]) -> bytes:
	packet = [
		p for p in cfg_packets
		if p.config_word == ConfigWord(PacketType.TYPE1, OPCode.WRITE, 1, register=Register.IDCODE)
	][0]
	return packet.payload


def read_init_packets(cfg_packets: list, init_packets: list) -> List[ConfigPacket]:
	for idx, packet in enumerate(cfg_packets):
		if (
				packet.config_word.register == Register.CMD and packet.payload == b'\x00\x00\x00\x01') or packet.config_word.register == Register.FAR:
			return cfg_packets[idx:]
		else:
			init_packets.append(packet)
	# Catching weird bitstreams
	raise Exception("Unexpected packet order, bitstream deemed incorrect")


def order_packets(cfg_packets: List[ConfigPacket], init_packets: list, frames: list, suffix_packets: list,
				  addr_gen: FrameAddressGenerator) -> None:
	"""
	The acceptance criteria of bitstreams of this function is very strict in order to prevent unpredictable bugs.
	Here the bitstream payload is seen as a sequence of "packet chunks".
	Below are the "main package flows":
		COMPRESSED:                    Partial:                    Full:
		Write FAR: addr         Write CMD: 1                Write FAR: addr
		Write CMD: 1            NOP                         Write CMD: 1
		NOP                     Write FAR: addr             NOP
		Write FDRI: 101 PW      NOP                         Write FDRI: 0 PW
		Write CMD: 2            Write FDRI: 0 PW            Type 2 Package: full payload
								Type 2 Package: payload
		12 x NOP
		Write MFWR: 8 x 0
		Write FAR: next addr
		Write MFWR: 8 x 0
		Write FAR: next addr
		Write MFWR: 8 x 0
		...
		Repeat until all frames with same content done


	Ofc compressed and partial can be combined.
	Compressed bitstreams can repeat the multiframe write (mfwr(egister)) multiple times for different frames,
	in the case that another frame (besides the zero frame) is repeated often in the bitstream.
	"Nope spacing" for compressed bitstreams can vary based on the region/column it is flashed to.

	Partial bitstreams are quite flexible. They may write to two regions that are rather far from each other.
	But the latter is theoretical and would need a specific nope spacing (which is why the latter is not implemented).

	These methods below may read compressed, full, partial and a combinations of the latter three formats, but
	The BSHandler can only write partial and full bitstreams.
	Also, the reading methods may reject some bitstreams with weird compressed/partial patterns,
	even if the bitstreams would work on the actual device.
	This has been the case for some blanking bitstream created by vivado.


	PW: Payload Words,
	Any other acronym can be looked up in the official AMD Xilinx documentation ug470
	"""
	cfg_packets = read_init_packets(cfg_packets, init_packets)
	cfg_packets = read_frame_data(cfg_packets, frames, addr_gen)
	suffix_packets += cfg_packets


def read_frame_data(cfg_packets: List[ConfigPacket], frames: list, addr_gen: FrameAddressGenerator) \
		-> List[ConfigPacket]:
	while True:
		if (cfg_packets[1].config_word.op_code == OPCode.NOP == cfg_packets[3].config_word.op_code
				and cfg_packets[2].config_word.register == Register.FAR
				and cfg_packets[4].config_word.register == Register.FDRI):
			addr_gen.set_start(int.from_bytes(cfg_packets[2].payload, "big"))
			cfg_packets = cfg_packets[4:]

		elif cfg_packets[2].config_word.op_code == OPCode.NOP and cfg_packets[
			0].config_word.register == Register.FAR and cfg_packets[3].config_word.register == Register.FDRI:

			addr_gen.set_start(int.from_bytes(cfg_packets[0].payload, "big"))
			cfg_packets = cfg_packets[3:]
		else:
			break

		type2_write = first_write_is_type2(cfg_packets)
		if type2_write:
			offset = 2
		else:
			offset = 1
		if cfg_packets[offset].config_word == ConfigWord(PacketType.TYPE1, OPCode.WRITE, 1, Register.CMD) and \
				cfg_packets[offset].payload == bytes.fromhex("00000007"):
			cfg_packets = read_uncompressed_chunk(addr_gen, cfg_packets, frames, offset)
		elif next_chunk_is_mfw(cfg_packets, type2_write):
			cfg_packets = read_mfw_chunk(addr_gen, cfg_packets, frames, offset)
		else:
			cfg_packets = read_uncompressed_chunk(addr_gen, cfg_packets, frames, offset)

	return cfg_packets


def next_chunk_is_mfw(cfg_packets: List[ConfigPacket], type2_write: bool) -> bool:
	if type2_write:
		cmd_idx = 2
	else:
		cmd_idx = 1
	# Check COMPRESSED
	if (cfg_packets[cmd_idx].config_word.register == Register.CMD
			and cfg_packets[cmd_idx].payload == b'\x00\x00\x00\x02'):
		return True
	elif ((cfg_packets[cmd_idx].config_word.register == Register.CMD and cfg_packets[
		cmd_idx].payload == b'\x00\x00\x00\x01')
		  or cfg_packets[cmd_idx].config_word.register == Register.CRC 
		  or cfg_packets[cmd_idx].config_word.register == Register.MASK):
		return False
	else:
		# Catching weird bitstreams
		raise Exception("Unexpected packet order, bitstream deemed incorrect")


def first_write_is_type2(cfg_packets: List[ConfigPacket]) -> bool:
	if cfg_packets[0].config_word == ConfigWord(PacketType.TYPE1, OPCode.WRITE, 0, Register.FDRI) and cfg_packets[
		1].config_word.packet_type == PacketType.TYPE2:
		return True
	elif cfg_packets[1].config_word == ConfigWord(PacketType.TYPE1, OPCode.WRITE, 1, Register.CMD):
		return False
	else:
		raise Exception("Unexpected payload size, bitstream deemed incorrect")


def read_mfw_chunk(addr_gen: FrameAddressGenerator, cfg_packets: List[ConfigPacket], frames: List[Frame],
				   offset: int) -> List[
	ConfigPacket]:
	frame_data = cfg_packets[offset - 1].payload
	# The first payload can actually contain multiple frames
	# Frames after the first one are send to adresses using auto increment
	# The last frame send to the FDRI will be the one that stays in the FDRI and is therefore used for MFWs
	frames += frames_from_payload(frame_data, addr_gen)
	frame_data = frame_data[-404:]

	if cfg_packets[16 + offset].config_word.op_code == OPCode.NOP:
		nop_spacing = 10
		start = 22 + offset
	elif cfg_packets[16 + offset].config_word.register == Register.FAR or cfg_packets[
		16 + offset].config_word.register == Register.CMD:
		nop_spacing = 2
		start = 14 + offset
	else:
		raise Exception("Unexpected packet order, bitstream deemed incorrect")

	for idx in range(start, len(cfg_packets), nop_spacing):
		if cfg_packets[idx].config_word.register == Register.FAR:
			frames.append(Frame.from_bytes(int.from_bytes(cfg_packets[idx].payload, "big"), frame_data))
		else:
			return cfg_packets[idx:]
	# Catching weird bitstreams
	raise Exception("Unexpected packet order, bitstream deemed incorrect")


def read_uncompressed_chunk(addr_gen: FrameAddressGenerator, cfg_packets: List[ConfigPacket], frames: List[Frame],
							offset: int) -> List[
	ConfigPacket]:
	payload = cfg_packets[offset - 1].payload

	if len(payload) % (101 * 4) != 0:
		# Catching weird bitstreams
		raise Exception("Unexpected payload size, bitstream deemed incorrect")
	else:
		frames += frames_from_payload(payload, addr_gen)
		return cfg_packets[offset:]


def frames_from_payload(payload: bytes, addr_gen: FrameAddressGenerator) -> List[Frame]:
	frames = []
	i = 0
	while i < len(payload):
		frames.append(Frame.from_bytes(next(addr_gen), payload[i: i + 101 * 4]))
		if addr_gen.padding_frames_needed:
			i += 3 * 4 * 101
		else:
			i += 4 * 101
	return frames


class PacketGenerator(object):
	"""
	Helper class that creates new packet on "next" call.
	Is initiated with bytes. The given bytes have to start after the sync word.
	"""

	def __init__(self, bs_bytes: bytes):
		self.idx = 0
		self.bs_bytes = bs_bytes
		self.max_idx = len(bs_bytes)

	def __iter__(self):
		return self

	def __next__(self):

		if self.idx < self.max_idx:
			cfgw_chunk = self.bs_bytes[self.idx: self.idx + 4]
			self.idx += 4

			config_word = ConfigWord.from_bytes(cfgw_chunk)

			if 4 * config_word.count > self.max_idx:
				raise Exception(f"Error in bitstream format. ConfigWord declares {config_word.count} data words, "
								f"which is not possible")
			payload = self.bs_bytes[self.idx: self.idx + (4 * config_word.count)]
			self.idx += (4 * config_word.count)
			return ConfigPacket(config_word, payload)
		else:
			return None
