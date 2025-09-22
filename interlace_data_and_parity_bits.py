import argparse
import pathlib

import numpy as np
import os

def create_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        "Combines a data and a parity bit read into one"
    )
    parser.add_argument(
        "-d", "--data_bits_file",
        help="Path to data bits read",
        type=pathlib.Path,
        required=True
        
    )
    parser.add_argument(
        "-p", "--parity_bits_file",
        help="Path to parity bits read",
        type=pathlib.Path,
        required=True
    )
    parser.add_argument(
        "-o", "--output",
        help="Path where interlaced/merged file shall be saved",
        type=pathlib.Path,
        required=True
    )
    parser.add_argument(
        "-f", "--fix_parity_inversion",
        action="store_true",
    )
    return parser




def merge_data_sets(data_bits: bytes, parity_bits: bytes, fix_parity_inversion: bool) -> bytes:
    """
    Probably not the most efficient and most numpy friendly implementation
    but it's sufficient for this task
    """

    data_numpy_array = np.unpackbits(
        np.array(
            [i for i in data_bits],
            dtype=np.uint8
        )
    )

    parity_numpy_array = np.unpackbits(
        np.array(
            [i for i in parity_bits],
            dtype=np.uint8
        )
    )

    if fix_parity_inversion:
        new_parity_bits = list()
        for idx in range(0, len(parity_numpy_array), 8):
            for i in range(4, 8):
                new_parity_bits.append(parity_numpy_array[idx+i])
            for i in range(0, 4):
                new_parity_bits.append(parity_numpy_array[idx+i])
        parity_numpy_array = np.array(
            new_parity_bits,
            dtype=np.uint8
        )


    assert len(data_bits)/8 == len(parity_bits)

    interlaced_bits = []
    for data_idx in range(0, len(data_numpy_array), 8):
        interlaced_bits += list(data_numpy_array[data_idx:data_idx+8])
        assert int(data_idx/8) == data_idx/8
        interlaced_bits.append(parity_numpy_array[int(data_idx/8)])
    interlaced_bits = np.array(interlaced_bits, dtype=np.uint8)

    interlaced_ints = np.packbits(interlaced_bits, bitorder="big")
    return interlaced_ints.tobytes()


def main(
    data_bits_file: pathlib.Path, 
    parity_bits_file: pathlib.Path,
    outpath: pathlib.Path,
    fix_parity_inversion: bool   
) -> None:
    
    with open(data_bits_file, mode="rb") as data_f:
        data_bytes = data_f.read()
    with open(parity_bits_file, mode="rb") as parity_f:
        parity_bytes = parity_f.read()

    interlaced_bytes = merge_data_sets(data_bytes, parity_bytes, fix_parity_inversion)

    if not outpath.parent.exists():
        os.makedirs(outpath.parent)
    with open(outpath, mode="wb") as out_f:
        out_f.write(interlaced_bytes)



if __name__ == "__main__":
    argparser  = create_argparser()
    args = vars(argparser.parse_args())
    main(args["data_bits_file"], args["parity_bits_file"], args["output"], args["fix_parity_inversion"])


