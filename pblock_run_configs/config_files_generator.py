import argparse
from pathlib import Path

argparser = argparse.ArgumentParser("Creates config.sh files for 'run_pblock_analysis.sh'")

argparser.add_argument(
    "-vp",
    "--vivado_project",
    help="Path to vivado project, used in config files",
    required=True
)
argparser.add_argument(
    "-v",
    "--vivado_path",
    help="Path to vivado executable",
    required=True
)
argparser.add_argument(
    "-ep",
    "--experiment_output_path",
    help="Path where experiment will save it's results and bitstreams",
    required=True
)
argparser.add_argument(
    "-r",
    "--reads",
    help="Number of reads performed during analysis",
    type=int,
    required=True
)
argparser.add_argument(
    "-o",
    "--output_path",
    help="Path where generated config files will be saved",
    required=True
)
argparser.add_argument(
    "-sn",
    "--uart_sn",
    help="Serial number of UART device used for reading",
    required=True
)
argparser.add_argument(
    "-i",
    "--programming_interface",
    help="Interface used for flashing the bitstream (used internally by vivado)",
    required=True
)
argparser.add_argument(
    "-b",
    "--board",
    help="Name of the board used",
    required=True
)
argparser.add_argument(
    "-f",
    "--fpga",
    help="Name of the used fpga device",
    required=True
)
argparser.add_argument(
    "-w",
    "--wait_time",
    help="Time that shall be waited between deactivating and reactivating brams",
    default=0,
    required=False,
    type=int
)
argparser.add_argument(
    "-pf",
    "--use_previous_value_ff",
    help="If used, bitstreams and reads with previous value ff will be performed",
    action="store_true"
)
argparser.add_argument(
    "-pmin",
    "--pblock_first_idx",
    help="First pblocks index (most often 1)",
    type=int,
    required=True
)
argparser.add_argument(
    "-pmax",
    "--pblock_last_idx",
    help="Index of last pblock",
    type=int,
    required=True
)
argparser.add_argument(
    "-x",
    "--x_index",
    help="x index of first bram block (index of bram column)",
    type=int,
    required=True
)
argparser.add_argument(
    "-y",
    "--y_index",
    help="y index of first bram block",
    type=int,
    required=True
)
argparser.add_argument(
    "-pr",
    "--pblock_per_row",
    help="Number of pblocks per row",
    type=int,
    required=True
)
argparser.add_argument(
    "-rc",
    "--row_count",
    help="Number of rows in fpga",
    type=int,
    required=True
)


def write_config_file(
output_path: Path,
                        vivado_path: Path,
                      vivado_project_path: Path,
                      pblock_idx: int,
                      x_pos: int,
                      y_min_pos: int,
                      reads: int,
                      uart_sn: str,
                      programming_interface: str,
                      fpga: str,
                      board: str,
                      experiment_output_path: Path,
                      wait_time: int = 0,
                      use_previous_value_ff=False
                      ) -> None:
    use_previous_value_str = "True" if use_previous_value_ff else ""
    with open(output_path, mode="w") as f:
        for line in [f'vivado_path="{vivado_path}"',
             f'vivado_project_path="{vivado_project_path}"',
             f'pblock="pblock_{pblock_idx}"',
             f'bram_row_x_position={x_pos}',
             f'bram36_min_y_position={y_min_pos}',
             f'bram36_max_y_position={y_min_pos + 11}',
             f'reads={reads}',
             f'output_path="{experiment_output_path}"',
             f'use_previous_value_ff="{use_previous_value_str}"',
             f'uart_sn="{uart_sn}"',
             f'programming_interface="{programming_interface}"',
             f'fpga="{fpga}"',
             f'board_name="{board}"',
             f'wait_time={wait_time}'
             ]:
            f.write(line+"\n")


if __name__ == "__main__":
    args = argparser.parse_args()

    current_row = args.y_index
    current_bram_column = args.x_index
    print(str(args))
    for pblock_idx in range(args.pblock_first_idx, args.pblock_last_idx + 1):
        print(current_bram_column, current_row)
        write_config_file(
            output_path=Path(args.output_path, f"{args.board}_pblock_{pblock_idx}.sh"),
            vivado_path=args.vivado_path,
            vivado_project_path=args.vivado_project,
            experiment_output_path=args.experiment_output_path,
            pblock_idx=pblock_idx,
            x_pos=current_bram_column,
            y_min_pos=(current_row) * 12,
            reads=args.reads,
            uart_sn=args.uart_sn,
            programming_interface=args.programming_interface,
            fpga=args.fpga,
            board=args.board,
            wait_time=args.wait_time,
            use_previous_value_ff=args.use_previous_value_ff
        )

        if current_bram_column == args.x_index - args.pblock_per_row + 1:
            current_bram_column = args.x_index
            current_row += 1

            if current_row > args.y_index + args.row_count:
                raise Exception("Reached last row before iterating through all pblocks. This shouldn't happen")
        else:
            current_bram_column -= 1
