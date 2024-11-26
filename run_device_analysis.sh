#!/usr/bin/env bash

# Function Definitions

#######################################
# Produces meta_data.json for device
# Globals:
#   None
# Arguments:
#   board_dir_path
#   board_name
#   fpga
#   uart_sn
#   programming_interface
#######################################
function write_board_meta_data_json(){
    board_meta_data_path="${1}/meta_data.json"
    if [ ! -f "${board_meta_data_path}" ]; then
        touch "${board_meta_data_path}"
        {
            printf "{\n"
            printf "\t\"board_name\":\"%s\",\n" "${2}"
            printf "\t\"fpga\":\"%s\",\n" "${3}" 
            printf "\t\"uart_sn\":\"%s\",\n" "${4}" 
            printf "\t\"programming_interface\":\"%s\",\n" "${5}"
            printf "\t\"date\":\"%s\"\n" "$(date +"%F-%T")"
            printf "}"
        } >> "${board_meta_data_path}"
    fi
} 

#######################################
# Produces meta_data.json for experiment
# Globals:
#   None
# Arguments:
#   board_dir_path
#   board_name
#   fpga
#   uart_sn
#   programming_interface
#######################################
function write_experiment_meta_data_json(){
    experiment_meta_data_path="${1}/meta_data.json"
    if [ ! -f "${experiment_meta_data_path}" ]; then
        touch "${experiment_meta_data_path}"
        {
            printf "{\n"
            printf "\t\"commit\":\"%s\"\n" "$(git rev-parse HEAD)"
            printf "}"
        } >> "${experiment_meta_data_path}"
    fi
} 

# Help output:
read -r -d '' help <<EOM
Meta Script that can potentially run analysis of an entire device
Calls "run_pblock_analysis.sh" over multiple pblocks
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
    uart_sn="A503VSXV"
    programming_interface="Digilent/25163300869FA"
    fpga="xczu1eg"
    board_name="te0802"

NOTE: Do not ever pass randomly scripts as arguments to this script. (arbitrary code exec)

Call with -c or --clean to remove directories for a given pblock
EOM

# "Parse" arguments
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    echo "$help"
    exit 0
elif [ "$1" == "-c" ] || [ "$1" == "--clean" ]; then
    # Remove directories for a given pblock configuration
    shift
    for config_file in "$@"
    do
        echo "${config_file}"
        source "${config_file}"
        rm -r "${output_path}/boards/${board_name}/${pblock}"
    done
    exit 0
fi

for config_file in "$@" 
do  
    echo "${config_file}"
    source "${config_file}"
    # Create meta data for experiment
    write_experiment_meta_data_json "${output_path}"

    # Create directory for board (if not available)
    if [ ! -d "${output_path}/boards/${board_name}" ]; then
        mkdir -p "${output_path}/boards/${board_name}"
    fi
    # Create meta data for board
    write_board_meta_data_json "${output_path}/boards/${board_name}" "${board_name}" "${fpga}" "${uart_sn}" "${programming_interface}"
    source run_pblock_analysis.sh "${vivado_path}" "${vivado_project_path}" \
    "${pblock}" "${bram_row_x_position}" "${bram36_min_y_position}" "${bram36_max_y_position}" \
    "${reads}" "${output_path}/boards/${board_name}" "${uart_sn}" "${programming_interface}" \
    "${use_previous_value_ff}" "${wait_time}" > "${output_path}/${pblock}_$(date +"%F-%T").log"
done
