#!/usr/bin/env bash

# Help output:
read -r -d '' help <<EOM
Script that automatizes BRAM readout of FPGA device.
Usage:
run_bram_analysis <vivado_project_path> <pblock_name> <bram_row_x_position> <bram36_min_y_position> <bram36_max_y_position> <output_path>

Please specify paths from the root directory '/'
EOM

# "Parse" arguments
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    echo "$help"
    exit 0
elif [ "$#" -ne 8 ]; then
    echo "Wrong number of arguments ${#}!\n"
    echo "$help"
else
    vivado_path=$1
    vivado_project_path=$2
    pblock=$3
    bram_row_x_position=$4
    bram36_min_y_position=$5
    bram36_max_y_position=$6
    reads=$7
    output_path=$8
fi

# Initiate path variables that depend on args
project_xpr=$(ls vivado_projects/project_1 | grep .xpr)

# NOTE: The paths below depend on the order of child implementation runs in vivado
#       Changing the implementation run in the dynamic eXchange wizard will change those dependencies
run_dir=$(ls "${vivado_project_path}" | grep .runs)
full_bs_with_initial_value_00="${vivado_project_path}/${run_dir}/child_0_impl_1/read_bram.bit"
full_bs_with_initial_value_ff="${vivado_project_path}/${run_dir}/child_1_impl_1/read_bram.bit"
bramless_partial_bs="${vivado_project_path}/${run_dir}/child_2_impl_1/bram_wrap_return_0_partial.bit"
partial_bram_bs="${vivado_project_path}/${run_dir}/child_0_impl_1/bram_wrap_bram_wrap_ff_partial.bit"
modified_bs="temp_bs.bin"
from_root="$(pwd)"


# Iterate over all BRAM Blocks between bram36_min and max_y (inclusive)
for current_bram_y_position in $(seq "$bram36_min_y_position" "$bram36_max_y_position"); do
    ram_block="RAMB36_X${bram_row_x_position}Y${current_bram_y_position}"

    # Create bitstreams using predefined tcl script
    "${vivado_path}" -mode batch -source synthesize_for_bram_block_x.tcl -tclargs "$project_xpr" "$pblock" "$bram_row_x_position" "$bram36_min_y_position" "$bram36_max_y_position" "$current_bram_y_position"

    # create modified bs:
    python initialize_bram/create_partial_initialization_bitstream.py -pb "${partial_bram_bs}" -ob "${modified_bs}" -a "heuristic" -ar "XCUS+"

    # Create directory where measurements are saved
    if [ ! -d "${output_path}/${pblock}/${ram_block}" ]; then
        mkdir "${output_path}/${pblock}/${ram_block}/0-to-f" "${output_path}/${pblock}/${ram_block}/f-to-0" "${output_path}/${pblock}/${ram_block}/bs"
    fi

    # With previous value 00:
    for read in $(seq 0 "$reads"); do
        # BRAM init + readout process
        "${vivado_path}" -mode batch -source "initialize_bram/flash_bitstreams.tcl" -tclargs "localhost:3121/xilinx_tcf/Digilent/25163300869FA" "${full_bs_with_initial_value_00}" "${bramless_partial_bs}" "${from_root}/${modified_bs}";
        python "reading/read_bram_ftdi.py" -d "A503VSXV" -v "00" -o "${output_path}/${pblock}/${ram_block}/0-to-f/${read}";
    done

    # With previous value ff:
    for read in $(seq 0 "$reads"); do
        # BRAM init + readout process
        "${vivado_path}" -mode batch -source "initialize_bram/flash_bitstreams.tcl" -tclargs "localhost:3121/xilinx_tcf/Digilent/25163300869FA" "${full_bs_with_initial_value_ff}" "${bramless_partial_bs}" "${from_root}/${modified_bs}";
        python "reading/read_bram_ftdi.py" -d "A503VSXV" -v "ff" -o "${output_path}/${pblock}/${ram_block}/f-to-0/${read}";
    done
    
    # Save bitstreams for debugging
    cp "$full_bs_with_initial_value_00" "${output_path}/${pblock}/${ram_block}/bs/${ram_block}_00.bit"
    cp "$full_bs_with_initial_value_ff" "${output_path}/${pblock}/${ram_block}/bs/${ram_block}_ff.bit"
    cp "$bramless_partial_bs"  "${output_path}/${pblock}/${ram_block}/bs/${ram_block}_bramless_partial.bit"
    cp "$partial_bram_bs"  "${output_path}/${pblock}/${ram_block}/bs/${ram_block}_partial_bram_bs.bit"
    cp "$modified_bs" "${output_path}/${pblock}/${ram_block}/bs/${ram_block}_modified_partial.bit"

done

# Remove modified bs
rm "${modified_bs}"
