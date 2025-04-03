import argparse
import enum
from pathlib import Path

class PatternType(enum.Enum):
    STRIPES = enum.auto()


def create_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Creates sample data used for tests."
        "Data is meant to imitate how real data may look"
    )
    parser.add_argument(
        "-t", "--type",
        help="What pattern shall the created mock data have?",
        choices=["STRIPES"],
        default=PatternType.STRIPES,
        type=PatternType
    )
    parser.add_argument(
        "-p", "--base_path",
        help="Path of top directory where data will be created. "
        "Data will be created as would the data of a real experiment would be",
        default="mock_experiment",
        type=Path
    )

    return parser

def create_single_mock_read(type: PatternType, path: Path, 
                            parity: bool = False) -> None:
    summed_pattern = None
    if type is PatternType.STRIPES:
        if parity == False:
            pattern = b'\x00' * 4 + b'\xff' * 8 + b'\x00' * 4
        else:
            pattern = b"\x0f\xf0" * 4
        summed_pattern = pattern * 4 * 64

    with open(path, mode="wb") as f:
        f.write(summed_pattern)    

def create_mock_temperature_file(path: Path) -> None:
    with open(path, mode="w") as f:
        f.write("#It's over 9000!\n9001\n")

def create_mock_experiment_json(path: Path) -> None:
    with open(path, mode="w") as f:
        f.write("{\n\"commit\":\"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\"\n}")

def create_mock_board_json(path: Path) -> None:
    with open(path, mode="w") as f:
        f.write(
            "{"
	            "\"board_name\":\"te0802\","
                "\"fpga\":\"xczu1eg\","
                "\"uart_sn\":\"A503VSXV\","
                "\"programming_interface\":\"Digilent/25163300869FA\","
                "\"date\":\"2024-11-27-15:18:11\""
            "}"
        )

def iterate_and_create_dirs(type: PatternType, path: Path) -> None:
    path.mkdir(exist_ok=True, parents=True)
    create_mock_experiment_json(Path(path, "meta_data.json"))
    board_path = Path(path, "boards", "some_board")
    board_path.mkdir(exist_ok=True, parents=True)
    create_mock_board_json(path=Path(board_path, "meta_data.json"))

    for clock_region_x in range(3):
        for column_y in range(3):
            pblock_name = f"pblock_{clock_region_x * 3 + column_y + 1}"
            for bram_z in range(12):
                bram_name = f"RAMB36_X{clock_region_x}Y{column_y * 12 + bram_z}"
                current_path = Path(
                    board_path, 
                    pblock_name, 
                    bram_name, 
                    "some_read_session"
                )
                current_path.mkdir(parents=True, exist_ok=True)
                data_read_path = Path(current_path, "data_reads")
                parity_read_path = Path(current_path, "parity_reads")
                temperature_path = Path(current_path, "temperature.txt")

                data_read_path.mkdir(parents=True, exist_ok=True)
                parity_read_path.mkdir(parents=True, exist_ok=True)
                create_mock_temperature_file(temperature_path)

                create_single_mock_read(
                    type=type,
                    path=Path(data_read_path, "1")
                )
                create_single_mock_read(
                    type=type,
                    path=Path(parity_read_path, "1"),
                    parity=True
                )

def main() -> None:
    parser = create_argparser()
    args = parser.parse_args()
    iterate_and_create_dirs(type=args.type, path=args.base_path)


if __name__ == "__main__":
    main()
