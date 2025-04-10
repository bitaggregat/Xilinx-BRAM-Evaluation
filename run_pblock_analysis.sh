#!/usr/bin/env bash

# Function definitions:

# trap ctrl-c and call ctrl_c()
trap ctrl_c INT

function ctrl_c() {
  echo "run_pblock_analysis was interrupted"
  tmux kill-session -t "${vivado_session}"
  echo "tried to kill vivado tmux session"
}

#######################################
# Constantly checks output of parallel tmux terminal
# The terminal is expected to run a vivado interpreter
# The function loops until the current vivado command has finished
# Globals:
#   None
# Arguments:
#   None
#######################################
function wait_for_tmux_vivado(){
    vivado_output=''
    while [ "${vivado_output}" != "Vivado%" ]; do
        sleep 0.01s
        # Get last line of capture
        vivado_output=$(tmux capture-pane -p -t "${vivado_session}" |sed '/^$/d' |tail -1);
    done
} 

#######################################
# Measures temperature from vivado terminal in tmux
# Appends measure to file
# Globals:
#   None
# Arguments:
#   temperature file: path to file where new temperature measurement is appended 
#######################################
function measure_temperature(){
    tmux send-keys -t "${vivado_session}" "puts [get_property TEMPERATURE [get_hw_sysmons]]" C-m;
    # Catch penultimate line of output (contains temperature values)
    temperature_str="Vivado%"
    while [[ "${temperature_str}" == *"Vivado%"* ]] || [[ ${#temperature_str} -gt 9 ]]; do
        temperature_str=$(tmux capture-pane -p -t "${vivado_session}" |sed '/^$/d'| tail -n 2|head -1);
    done
    echo "${temperature_str}" >> "${1}";
}

#######################################
# Flashes bitstreams to fpga via vivado terminal in tmux
# This prepares the bram for a measurement
# Globals:
#   None
# Arguments:
#   full bs: Configures fpga with uart and fills bram with either 00 or ff
#   bramless_partial_bs: Reconfigures fpga to deactivate bram
#   modified_bs: Reactivates bram but without values
#   wait_time: Time that will be waited (in s) before reactivating the bram
#######################################
function flash_bitstreams(){
    tmux send-keys -t "${vivado_session}" "set_property PROGRAM.FILE ${1} [current_hw_device]" C-m "program_hw_devices [current_hw_device]" C-m
    wait_for_tmux_vivado
    tmux send-keys -t "${vivado_session}" "set_property PROGRAM.FILE ${2} [current_hw_device]" C-m "program_hw_devices [current_hw_device]" C-m
    wait_for_tmux_vivado
    echo "waiting for ${4:-0}s"
    sleep "${4:-0}"s
    tmux send-keys -t "${vivado_session}" "set_property PROGRAM.FILE ${3} [current_hw_device]" C-m "program_hw_devices [current_hw_device]" C-m
    wait_for_tmux_vivado
}

#######################################
#######################################
# MAIN START:
#######################################
#######################################


# Help output:
read -r -d '' help <<EOM
Script that automatizes BRAM readout of FPGA device.
Can read out all BRAMs in a pblock
Usage:
run_bram_analysis <vivado_project_path> <pblock_name> <bram_row_x_position> <bram36_min_y_position> <bram36_max_y_position> <output_path> <uart_sn> <programming_interface> [use_previous_value_ff] [wait_time]

Please specify paths from the root directory '/'
EOM

# "Parse" arguments
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    echo "$help"
    exit 0
elif [ "$#" -lt 10 ]; then
    echo "Wrong number of arguments ${#}!"
    echo "$help"
    exit 1
else
    vivado_path=$1
    vivado_project_path=$2
    pblock=$3
    bram_row_x_position=$4
    bram36_min_y_position=$5
    bram36_max_y_position=$6
    reads=$7
    output_path=$8
    uart_sn=$9
    programming_interface=${10}
    use_previous_value_ff=${11}
    wait_time=${12}
fi

# Initiate path variables that depend on args
project_xpr="${vivado_project_path}/$(ls "$vivado_project_path" | grep .xpr)"

# NOTE: The paths below depend on the order of child implementation runs in vivado
#       Changing the implementation run in the dynamic eXchange wizard will change those dependencies
run_dir=$(ls "${vivado_project_path}" | grep .runs)
full_bs_with_initial_value_00="${vivado_project_path}/${run_dir}/child_0_impl_1/read_bram.bit"
full_bs_with_initial_value_ff="${vivado_project_path}/${run_dir}/child_1_impl_1/read_bram.bit"
bramless_partial_bs="${vivado_project_path}/${run_dir}/child_2_impl_1/bram_wrap_return_0_${pblock}_partial.bit"
partial_bram_bs="${vivado_project_path}/${run_dir}/child_1_impl_1/bram_wrap_bram_wrap_ff_${pblock}_partial.bit"
modified_bs="temp_bs.bin"
from_root="$(pwd)"

# Initialize tmux vivado session, used for:
# - flashing bs
# - measuring temperature
# without open/close hw manager overhead
vivado_session="vivado_${uart_sn}_${pblock}"

# Kill previous vivado session if necessary
tmux kill-session -t "${vivado_session}"

tmux new-session -d -s "${vivado_session}"
# Open vivado interactive terminal in tmux
tmux send-keys -t "${vivado_session}" "${vivado_path} -mode tcl" C-m
# TODO describe bram measurement
if  [ "$reads" -gt 0 ]; then
  tmux send-keys -t "${vivado_session}" "open_hw_manager" C-m
  tmux send-keys -t "${vivado_session}" "connect_hw_server" C-m
  tmux send-keys -t "${vivado_session}" "current_hw_target \"localhost:3121/xilinx_tcf/${programming_interface}\"" C-m
  tmux send-keys -t "${vivado_session}" "open_hw_target" C-m
  # Wait for preparation script to finish
  wait_for_tmux_vivado
fi

# Iterate over all BRAM Blocks between bram36_min and max_y (inclusive)
for current_bram_y_position in $(seq "$bram36_min_y_position" "$bram36_max_y_position"); do
    ram_block="RAMB36_X${bram_row_x_position}Y${current_bram_y_position}"
    echo "${ram_block}"

    # Create directory where measurements are saved
    if [ ! -d "${output_path}/${pblock}/${ram_block}" ]; then
        mkdir -p "${output_path}/${pblock}/${ram_block}";
    fi

        
    # Synthethize and save bitstreams if bs dir does not exist
    if [ ! -d "${output_path}/${pblock}/${ram_block}/bs" ]; then
        mkdir "${output_path}/${pblock}/${ram_block}/bs"

        # Create bitstreams using predefined tcl script
        #echo "${vivado_path} -mode batch -source synthesize_for_bram_block_x.tcl -tclargs ${project_xpr} ${pblock} ${bram_row_x_position} ${bram36_min_y_position} ${bram36_max_y_position} ${current_bram_y_position}"
        "${vivado_path}" -mode batch -source tcl_scripts/synthesize_for_bram_block_x.tcl -tclargs "$project_xpr" "$pblock" "$bram_row_x_position" "$bram36_min_y_position" "$bram36_max_y_position" "$current_bram_y_position" > "${output_path}/${pblock}/${ram_block}/vivado.log"

        # create modified bs:
        python3 initialize_bram/create_partial_initialization_bitstream.py -pb "${partial_bram_bs}" -ob "${modified_bs}" -a "heuristic" -ar "XCUS+";

        cp "${full_bs_with_initial_value_00}" "${output_path}/${pblock}/${ram_block}/bs/${ram_block}_00.bit"
        cp "${full_bs_with_initial_value_ff}" "${output_path}/${pblock}/${ram_block}/bs/${ram_block}_ff.bit"
        cp "${bramless_partial_bs}"  "${output_path}/${pblock}/${ram_block}/bs/${ram_block}_bramless_partial.bit"
        cp "${partial_bram_bs}"  "${output_path}/${pblock}/${ram_block}/bs/${ram_block}_partial_bram_bs.bit"
        cp "${modified_bs}" "${output_path}/${pblock}/${ram_block}/bs/${ram_block}_modified_partial.bin"
        # Remove temporary bitstream
        rm "${modified_bs}";
    fi
    # Set bitstream paths to experiment directory ones
    full_bs_with_initial_value_00_local="${output_path}/${pblock}/${ram_block}/bs/${ram_block}_00.bit"
    full_bs_with_initial_value_ff_local="${output_path}/${pblock}/${ram_block}/bs/${ram_block}_ff.bit"
    bramless_partial_bs_local="${output_path}/${pblock}/${ram_block}/bs/${ram_block}_bramless_partial.bit"
    partial_bram_bs_local="${output_path}/${pblock}/${ram_block}/bs/${ram_block}_partial_bram_bs.bit"
    modified_bs_local="${output_path}/${pblock}/${ram_block}/bs/${ram_block}_modified_partial.bin"


    # Create temperature file for "previous_value_00"
    mkdir "${output_path}/${pblock}/${ram_block}/previous_value_00_t=${wait_time}"
    temperature_file_path_00="${output_path}/${pblock}/${ram_block}/previous_value_00_t=${wait_time}/temperature.txt";
    if [ ! -f "${temperature_file_path_00}" ]; then
        touch "${temperature_file_path_00}";
        echo "# Temperature in Celsius" >> "${temperature_file_path_00}";
    fi
    # Create temperature file for "previous_value_ff"
    if [ -n "${use_previous_value_ff}" ]; then
        mkdir "${output_path}/${pblock}/${ram_block}/previous_value_ff_t=${wait_time}"
        temperature_file_path_ff="${output_path}/${pblock}/${ram_block}/previous_value_ff_t=${wait_time}/temperature.txt";
        if [ ! -f "${temperature_file_path_ff}" ]; then
            touch "${temperature_file_path_ff}";
            echo "# Temperature in Celsius" >> "${temperature_file_path_ff}";
        fi
    fi

    
    for read in $(seq 1 "$reads"); do
        # With previous value 00:
        # BRAM init
        flash_bitstreams "${full_bs_with_initial_value_00_local}" "${bramless_partial_bs_local}" "${modified_bs_local}" "${wait_time}";
        # Readout process
        python3 "reading/read_bram_ftdi.py" -d "${uart_sn}" -o "${output_path}/${pblock}/${ram_block}/previous_value_00_t=${wait_time}/${read}";
        
        measure_temperature "${temperature_file_path_00}";

        if [ -n "${use_previous_value_ff}" ]; then
            # With previous value ff:
            # BRAM init 
            flash_bitstreams "${full_bs_with_initial_value_ff_local}" "${bramless_partial_bs_local}" "${modified_bs_local}" "${wait_time}";
            # Readout process
            python3 "reading/read_bram_ftdi.py" -d "${uart_sn}" -o "${output_path}/${pblock}/${ram_block}/previous_value_ff_t=${wait_time}/${read}";
                
            measure_temperature "${temperature_file_path_ff}";
        fi

    done
done

echo $(tmux capture-pane -pt "${vivado_session}")
tmux send-keys -t "${vivado_session}" "source tcl_scripts/clean_up_vivado.tcl" C-m
tmux kill-session -t "${vivado_session}"
