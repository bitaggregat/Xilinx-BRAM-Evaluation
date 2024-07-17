from functools import lru_cache
from typing import List

import numpy as np

from config_packet import ConfigPacket, ConfigWord, PacketType, OPCode, Register

'''
These are preset headers/init and footer/suffix packets which are needed for writing bitstreams
They were created by analysing bitstreams created by vivado

Additional notes on packets:
- ConfigPacket(CommonWords.WRITE_CMD, bytes.fromhex("0x00000007")) seems to be a placeholder for crc checks
    as it resets the crc register and is sometimes (based on vivado settings) replaced by a crc register write
'''


def sw_header(payload_footer_len: int, part: bytes = bytes.fromhex("3761333574637067323336")) -> bytes:
	'''
	Sources for explanation:
	http://www.fpga-faq.com/FAQ_Pages/0026_Tell_me_about_bit_files.htm
	ug470_7Series_Config: Chapter 5: Bitstream Composition
	'''
	part_len = (len(part) + 1).to_bytes(2, byteorder="big")

	header = (
			bytes.fromhex(
				'0009'
				'0ff00ff0  0ff00ff0  00'  # Unknown header
				'0001'  # 1 byte
				'61'  # a
				'0004'  # number of bytes of design name
				'c0bea000'  # Design name, can be changed to anything (always include a trailing 00 though)
			)
			+ bytes.fromhex("62") + part_len + part + b'\x00'  # Device name length and name
			+ bytes.fromhex("63") + b'\x00\x05\x44\x61\x74\x65\x00'  # Insert date here if needed
			+ bytes.fromhex("64") + b'\x00\x05\x54\x69\x6d\x65\x00'  # Insert time here if needed
			+ bytes.fromhex("65") + (payload_footer_len + 21 * 4).to_bytes(4,
																		   byteorder="big")  # len(bus detect + synch w + config packages)
			+ bytes.fromhex("ffffffff") * 16  # Dummy words
			+ bytes.fromhex("000000BB 11220044")  # Bus auto-detection words
			+ bytes.fromhex("ffffffff") * 2  # Dummy pad words
			+ bytes.fromhex("AA995566")  # Synch word
	)

	return header


class CommonWords:
	NOP = ConfigWord.from_bytes(bytes.fromhex("20000000"))
	WRITE_CMD = ConfigWord(PacketType.TYPE1, OPCode.WRITE, 1, register=Register.CMD)
	WRITE_MASK = ConfigWord(PacketType.TYPE1, OPCode.WRITE, 1, register=Register.MASK)
	WRITE_FAR = ConfigWord(PacketType.TYPE1, OPCode.WRITE, 1, register=Register.FAR)

	@staticmethod
	def write_type2(word_count: int) -> ConfigWord:
		return ConfigWord(PacketType.TYPE2, OPCode.WRITE, word_count)


class CommonPackets:
	SET_CMD_1 = ConfigPacket(CommonWords.WRITE_CMD, bytes.fromhex("00000001"))
	FDRI_FULLW_PREP = ConfigPacket(ConfigWord(PacketType.TYPE1, OPCode.WRITE, 0, register=Register.FDRI), b"")

	@staticmethod
	def set_far(frame_addr: int) -> ConfigPacket:
		return ConfigPacket(CommonWords.WRITE_FAR, [np.uint32(frame_addr)])


def full_init_packets(compressed: bool, part_idcode: bytes = b'\x03b\xd0\x93') -> List[ConfigPacket]:
	zero_payload = bytes.fromhex("00000000")
	nop = ConfigPacket(CommonWords.NOP, b'')

	return (
			[
				nop,
				ConfigPacket(ConfigWord(PacketType.TYPE1, OPCode.WRITE, 1, register=Register.TIMER), zero_payload),
				ConfigPacket(ConfigWord(PacketType.TYPE1, OPCode.WRITE, 1, register=Register.WBSTAR), zero_payload),
				ConfigPacket(CommonWords.WRITE_CMD, zero_payload),
				nop,
				ConfigPacket(CommonWords.WRITE_CMD, bytes.fromhex("00000007")),
				nop,
				nop,
				ConfigPacket(ConfigWord(PacketType.TYPE1, OPCode.WRITE, 1, register=Register.RBCRC_SW), zero_payload),
				ConfigPacket(ConfigWord(PacketType.TYPE1, OPCode.WRITE, 1, register=Register.COR0), b'\x02\x00?\xe5'),
				ConfigPacket(ConfigWord(PacketType.TYPE1, OPCode.WRITE, 1, register=Register.COR1), zero_payload),
				ConfigPacket(ConfigWord(PacketType.TYPE1, OPCode.WRITE, 1, register=Register.IDCODE), part_idcode),
				ConfigPacket(CommonWords.WRITE_CMD, bytes.fromhex("00000009")),
				nop,
				ConfigPacket(CommonWords.WRITE_MASK, b'\x00\x00\x04\x01'),
				ConfigPacket(ConfigWord(PacketType.TYPE1, OPCode.WRITE, 1, register=Register.CTL0),
							 b'\x00\x00\x05\x01'),
				ConfigPacket(CommonWords.WRITE_MASK, bytes.fromhex("00001000") if compressed else zero_payload),
				ConfigPacket(ConfigWord(PacketType.TYPE1, OPCode.WRITE, 1, register=Register.CTL1),
							 bytes.fromhex("00001000") if compressed else zero_payload),
			]
			+ [nop] * 8
	)


def full_suffix_packets(compressed: bool) -> List[ConfigPacket]:
	zero_payload = bytes.fromhex("00000000")
	nop = ConfigPacket(CommonWords.NOP, b'')

	return (
			[
				ConfigPacket(CommonWords.WRITE_CMD, bytes.fromhex("00000007")),
				nop,
				nop,
				ConfigPacket(CommonWords.WRITE_CMD, bytes.fromhex("0000000a")),
				nop,
				ConfigPacket(CommonWords.WRITE_CMD, bytes.fromhex("00000003")),
			] +
			(
				[
					ConfigPacket(CommonWords.WRITE_MASK, bytes.fromhex("00001000")),
					ConfigPacket(ConfigWord(PacketType.TYPE1, OPCode.WRITE, 1, register=Register.CTL1), zero_payload)
				]
				if compressed else []
			)
			+ [nop] * 100
			+
			[
				ConfigPacket(CommonWords.WRITE_CMD, bytes.fromhex("00000005")),
				nop,
				ConfigPacket(ConfigWord(PacketType.TYPE1, OPCode.WRITE, 1, register=Register.FAR), b'\x03\xbe\x00\x00'),
				ConfigPacket(CommonWords.WRITE_MASK, b'\x00\x00\x05\x01'),
				ConfigPacket(ConfigWord(PacketType.TYPE1, OPCode.WRITE, 1, register=Register.CTL0),
							 b'\x00\x00\x05\x01'),
				ConfigPacket(CommonWords.WRITE_CMD, bytes.fromhex("00000007")),
				nop,
				nop,
				ConfigPacket(CommonWords.WRITE_CMD, bytes.fromhex("0000000d"))
			]
			+ [nop] * 500
	)


def partial_init_packets(part_idcode: bytes = b'\x03b\xd0\x93') -> List[ConfigPacket]:
	nop = ConfigPacket(CommonWords.NOP, b'')
	zero_payload = bytes.fromhex("00000000")

	return (
			[nop] * 100 +
			[
				ConfigPacket(CommonWords.WRITE_CMD, bytes.fromhex("00000007")),
				nop,
				nop,
				ConfigPacket(ConfigWord(PacketType.TYPE1, OPCode.WRITE, 1, register=Register.IDCODE), part_idcode),
				ConfigPacket(CommonWords.WRITE_CMD, zero_payload),
				ConfigPacket(CommonWords.WRITE_MASK, bytes.fromhex("00000400")),
				ConfigPacket(ConfigWord(PacketType.TYPE1, OPCode.WRITE, 1, register=Register.CTL0),
							 bytes.fromhex("00000400")),
				ConfigPacket(CommonWords.WRITE_MASK, bytes.fromhex("00020000")),
				ConfigPacket(ConfigWord(PacketType.TYPE1, OPCode.WRITE, 1, register=Register.CTL1),
							 bytes.fromhex("00000000"))
			]
	)


@lru_cache(maxsize=1)
def partial_suffix_packets() -> List[ConfigPacket]:
	# zero_payload = bytes.fromhex("00000000")
	nop = ConfigPacket(CommonWords.NOP, b'')

	return (
			[
				nop,
				ConfigPacket(CommonWords.WRITE_MASK, bytes.fromhex("00000100")),
				ConfigPacket(ConfigWord(PacketType.TYPE1, OPCode.WRITE, 1, register=Register.CTL0),
							 bytes.fromhex("00000100")),
				ConfigPacket(CommonWords.WRITE_CMD, bytes.fromhex("00000003")),
			]
			+ [nop] * 100
			+
			[
				ConfigPacket(CommonWords.WRITE_CMD, bytes.fromhex("00000005")),
				nop,
				ConfigPacket(ConfigWord(PacketType.TYPE1, OPCode.WRITE, 1, register=Register.FAR), b'\x03\xbe\x00\x00'),
				nop,
				nop,
				ConfigPacket(CommonWords.WRITE_CMD, bytes.fromhex("00000007")),
				nop,
				ConfigPacket(CommonWords.WRITE_CMD, bytes.fromhex("0000000d"))
			]
			#+ [nop] * 200  # less than 200 according to byteman
	)
