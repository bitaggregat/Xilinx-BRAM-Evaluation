#!/usr/bin/env bash

echo "Note: This script is supposed to be run from */pblock_run_configs"

# Adapt this according to your target runs
python3 config_files_generator.py \
--vivado_project "$(dirname "${PWD}")/vivado_project/zcu102_eva_kit/read_bram_zcu102" \
--vivado_path /opt/Xilinx/Vivado/2024.1/bin/vivado \
--experiment_output_path "$(dirname "${PWD}")/measurements/automatic/full_scan_zcu102" \
--reads 0 \
--output_path zcu102_part2 \
--uart_sn A503VYYY \
--programming_interface "Digilent/210308B76F0D" \
--board zcu102_eva_kit \
--fpga xczu9eg \
--use_previous_value_ff \
--pblock_first_idx 57 \
--pblock_last_idx 76 \
--x_index 4 \
--y_index 3 \
--pblock_per_row 5 \
--row_count 4 \

