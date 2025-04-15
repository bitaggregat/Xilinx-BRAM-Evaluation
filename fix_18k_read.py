import argparse
from pathlib import Path


def create_argparser() -> argparse.ArgumentParser:
    argparser = argparse.ArgumentParser(
        description="Removes zeros from 18k bram reads that were read as 36k"
    )
    argparser.add_argument(
        "-i", "--in_path",
        help="Path of read file that needs to be fixed"
    )
    argparser.add_argument(
        "-o", "--out_path",
        help="Path where fixed read shall be saved"
    )
    return argparser

def load_file(path: Path) -> bytes:
    with open(path, mode="rb") as f:
        return f.read()
    
def fix_read(read: bytes) -> bytes:
    return b"".join([
        read[i].to_bytes(length=1) for i in range(0, len(read))
        if i % 4 == 0 or i % 4 == 1
    ])

def main(
    in_path: Path, out_path: Path
) -> None:
    read = load_file(in_path)
    fixed_read = fix_read(read)

    with open(out_path, mode="wb") as f:
        f.write(fixed_read)

if __name__ == "__main__":
    argparser = create_argparser()
    args = vars(argparser.parse_args())
    main(args["in_path"], args["out_path"])