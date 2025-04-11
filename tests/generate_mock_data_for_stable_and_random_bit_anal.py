import argparse
import random
from pathlib import Path




def create_argparser() -> argparse.ArgumentParser:
    argparser = argparse.ArgumentParser(
        description="Creates data set of mock reads of a single bram block." \
        "These shall be used to test scripts that separate random and stable bits"
    )

    argparser.add_argument(
        "-o", "--output_path",
        help="Path where mock data shall be saved",
        type=Path
    )

    argparser.add_argument(
        "-b", "--bram_block",
        help="Name of mocked bram block. " \
        "A directory of the same name will be created",
        required=False,
        default="RAMB36_X0Y0"
    )
    return argparser

def create_mock_temperature_file(path: Path) -> None:
    """
    Code duplicate from "generate_mock_data_sample.py"
    """
    with open(path, mode="w") as f:
        f.write("#It's over 9000!\n9001\n")

def create_pseudo_random_values_per_index(
    n: int, length: int, stable: float, unstable: float, random_stable: float
) -> list[int]:

    probability_values = list()
    for index in range(length):
        volatility_class = index % 4
        match volatility_class:
            case 0:
                stripe_index = index % 16
                # First 32 bytes and last 32 bytes of 128 block will be type 1
                # Middle part (index 64 - 96) will be type 2
                if 4 <= stripe_index < 12:
                    probability_values.append(0)
                else:
                    probability_values.append(n)
            case 1:
                probability_values.append(
                    random.randint(
                        unstable * n,
                        n - 1
                    )
                )
            case 2:
                probability_values.append(
                    random.randint(
                        (1-random_stable) * n,
                        random_stable * n - 1
                    )
                )
                print(1-random_stable)
                print(random_stable * n - 1)
            case 3:
                probability_values.append(
                    random.randint(
                        1,
                        (1-unstable) * n
                    )
                )
    return probability_values


def create_mock_byte_strings(
        n: int
) -> list[bytes]:
    """
    So the goal of this function is to:
        - create n byte strings of length 4096
        - single bytes will either be ff or 00 (for simplification)
        - we predetermine for each byte index the "volatility"
        - every byte with index % 3 == 0 will be stable
        - every byte with index % 3 == 1 will have 0.4 <= p(v=1) <= 0.6
        - every byte with index % 3 == 2 will have 0.25 <= p(v=1) <= 0.75
        - additionally the stable bytes will emulate a stripe pattern
    """

    length = 4096
    stable = 1
    unstable = 0.75
    random_stable = 0.6

    probability_values = create_pseudo_random_values_per_index(
        n, length, stable, unstable, random_stable
    )

    print(probability_values)
    print(probability_values[:16])
    print(probability_values[16:32])
    byte_strings = list()
    for _ in range(n):
        byte_string = b""
        for byte_index in range(length):
            if probability_values[byte_index] > 0:
                byte_string += b'\xff'
                probability_values[byte_index] -= 1
            else:
                byte_string += b'\x00'
        byte_strings.append(byte_string)

    return byte_strings


def main() -> None:
    argparser = create_argparser()
    args = vars(argparser.parse_args())

    byte_strings = create_mock_byte_strings(n=1000)
    
    target_dir = Path(args["output_path"], args["bram_block"])
    target_dir.mkdir(parents=True, exist_ok=True)

    create_mock_temperature_file(
        Path(target_dir, "temperature.txt")    
    )

    data_reads_path = Path(target_dir, "data_reads")
    parity_reads_path = Path(target_dir, "parity_reads")
    parity_reads_path.mkdir(exist_ok=True)
    data_reads_path.mkdir(exist_ok=True)

    for index, byte_string in enumerate(byte_strings):
        with open(Path(data_reads_path, str(index+1)), mode="wb") as data_read:
            data_read.write(byte_string)

        with open(Path(parity_reads_path, str(index+1)), mode="wb") as parity_read:
            for j in range(0, 4096, 8):
                parity_read.write(byte_string[j].to_bytes(length=1))

if __name__ == "__main__":
    main()

