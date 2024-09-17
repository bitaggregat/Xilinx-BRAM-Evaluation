#!/usr/bin/env bash

# Help output:
read -r -d '' help <<EOM
Meta Script that calls "run_bram_analysis.sh" over multiple pblocks
Expects a config file for each pblock.
The config file should be a bash script that defines variables in the following form:
    vivado_path="~/my/vivado/path"
    vivado_project_path="~/my/project/path"
    pblock="pblock_name"
    bram_row_x_position=10
    bram36_min_y_position=10
    bram36_max_y_position=17
    reads=1000
    output_path="~/my/output/path"

NOTE: Do not ever pass randomly scripts as arguments to this script. (arbitrary code exec)
EOM

# "Parse" arguments
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    echo "$help"
    exit 0
fi

for config_file in "$@" 
do
    echo "${config_file}"
    source "${config_file}"
    source run_bram_analysis.sh "${vivado_path}" "${vivado_project_path}" "${pblock}" "${bram_row_x_position}" "${bram36_min_y_position}" "${bram36_max_y_position}" "${reads}" "${output_path}"
done