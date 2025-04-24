import argparse
import pathlib
from typing import Type

def create_argparser() -> argparse.ArgumentParser:
    argparser = argparse.ArgumentParser(
        "Script takes run_pblock_analysis config file and modifies it.\n"
        "This is supposed to be used in combination with '*' via bash in " \
        "order to badges of config files quickly."
    )
    argparser.add_argument(
        "config_file",
        help="Config file that shall be changed",
        nargs="+"
    )

    argparser.add_argument(
        "-i", "--inplace",
        help="Overwrite input config file with new content",
        required=False,
        default=False,
        action="store_true"
    )

    argparser.add_argument(
        "-o", "--output_file",
        help="Path where new config file shall be saved. Will be ignored " \
        "if --inplace is True",
        required=False,
        type=pathlib.Path,
        default=None
    )

    argparser.add_argument(
        "-a", "--attribute",
        help="Attribute of config file that shall be changed. " \
        "Only one value can be changed at a time"
    )

    argparser.add_argument(
        "-n", "--new_value",
        help="New value that the selected attribute shall take"
    )

    return argparser


def check_attribute(attribute: str) -> Type:
    """
    Check if the given attribute is viable.
    Returns type of attribute (either int or str) if valid.
    Returns None if given attribute key is invalid
    """

    match attribute:
        case (
            "vivado_path" 
            | "vivado_project_path" 
            | "pblock" 
            | "output_path"
            | "programming_interface"
            | "fpga"
            | "uart_sn"
            | "board_name"
            | "use_previous_value_ff"
        ):
            return str
        case (
            "bram_row_x_position"
            | "bram36_min_y_position"
            | "bram36_max_y_position"
            | "reads"
            | "wait_time"
        ):
            return int
        case _:
            return None



def remove_attribute_from_list(
    config_file_lines: list[str],
    attribute: str
) -> bool:
    """
    Takes config file as lines as input.
    Searches for attribute in lines and removes said attribute.
    Will return False if attribute wasn't found in file
    """

    # Probably not the most efficient. But sufficient for this scope.
    indices = [
        idx for idx, line in enumerate(config_file_lines)
        if line.split("=")[0].strip() == attribute
    ]

    match len(indices):
        case 0:
            return False
        case 1:
            config_file_lines.pop(indices[0])
            return True
        case _:
            raise Exception(
                f"Somehow attribute '{attribute}' was present multiple times "
                "in config file. That's a big problem."
            )
    
def add_new_attribute(
        config_file_lines: list[str],
        attribute: str,
        attribute_type: Type,
        new_value: str
):
    if attribute_type is int:
        new_line = f"{attribute}={new_value}\n"
    elif attribute_type is str:
        new_line = f'{attribute}="{new_value}"\n'
    else:
        raise Exception(f"Got unexpected attribute_type {attribute_type}")
    
    config_file_lines.append(new_line)


def main(
    config_file: pathlib.Path,
    inplace: bool,
    output_file: pathlib.Path,
    attribute: str,
    new_value: str
):
    print(config_file)
    with open(config_file) as f:
        lines = f.readlines()

    attribute_type = check_attribute(attribute)

    remove_attribute_from_list(
        config_file_lines=lines,
        attribute=attribute
    )

    add_new_attribute(
        config_file_lines=lines,
        attribute=attribute,
        attribute_type=attribute_type,
        new_value=new_value
    )

    if inplace:
        with open(config_file, mode="w") as f:
            f.write("".join(lines))
    elif output_file is not None:
        with open(output_file, mode="w") as f:
            f.write("".join(lines))
    else:
        raise Exception(
            "No output file path was given." \
            "Either pass a output file path or use --inplace"
        )
    

if __name__ == "__main__":
    arparser = create_argparser()
    args = vars(arparser.parse_args())
    for config_file in args["config_file"]:
        sub_args = args.copy()
        sub_args["config_file"] = pathlib.Path(config_file)
        main(**sub_args)