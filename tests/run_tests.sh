#!/usr/bin/env bash

if [ "$#" -ne 1 ]; then
    echo "Wrong number of arguments ${#}!"
    exit 0
else
    source $1
fi

#######################################
# Temperature test
# Sometimes run_bram_analysis.sh tried to read temperature from tmux
#   before it was displayed by vivado
#######################################
#source run_bram_analysis.sh "${vivado_path}" "${vivado_project_path}" "pblock_1" 2 12 12 100 "tests/temp_dir"

# Verify content of temperature files
while IFS= read -r line || [[ -n "$line" ]]; do
    # Ignore comments
    if [[ "${line}" == "#"* ]]; then
        continue
    elif [ ${#line} -gt 9 ] || [[ ! $line =~ ^[0-9\.[:space:]]+$ ]]; then
        echo $line
        echo "Temperature test failed"
        exit 0
    fi
done < "tests/temp_dir/pblock_1/RAMB36_X2Y12/previous_value_ff/temperature.txt"

while IFS= read -r line || [[ -n "$line" ]]; do
    # Ignore comments
    if [[ "${line}" == "#"* ]]; then
        continue
    elif [ ${#line} -gt 9 ] || [[ ! $line =~ ^[0-9\.[:space:]]+$ ]]; then
        echo $line
        echo "Temperature test failed"
        exit 0
    fi
done < "tests/temp_dir/pblock_1/RAMB36_X2Y12/previous_value_00/temperature.txt"

echo "Tests succeeded"
