#!/usr/bin/env bash

# Adapt if necessary
vivado_path="/opt/Xilinx/Vivado/2024.1/bin/vivado"
vivado_project_path="$(dirname "${PWD}")/vivado_project/te0802/read_bram_te0802"
output_path="$(dirname "${PWD}")/tests/temp_dir"
pblock="pblock_1"
bram_row_x_position=2
bram36_min_y_position=12
bram36_max_y_position=13
reads=10
use_previous_value_ff="True"
uart_sn="A503VSXV"
programming_interface="Digilent/25163300869FA"
fpga="xczu1eg"
board_name="te0802"
wait_time=0
