#!/usr/bin/env bash

vivado_path="/tools/Xilinx/Vivado/2024.1/bin/vivado"
vivado_project_path="/home/kiya/Repos/temp/xilinx-bram-evaluation/vivado_project/te0802/read_bram_te0802"
pblock="pblock_1"
bram_row_x_position=2
bram36_min_y_position=12
bram36_max_y_position=23
reads=1000
output_path="/home/kiya/Repos/temp/xilinx-bram-evaluation/measurements/auto/verification"
programming_interface="Digilent/25163300869FA"
fpga="xczu1eg"
uart_sn="A801TJLF"
board_name="te0802"
use_previous_value_ff="True"
wait_time=0
