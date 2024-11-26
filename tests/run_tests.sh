#!/usr/bin/env bash


# Test run
# Tests will verify content produced by this run:
source run_device_analysis.sh tests/test_data/test_pblock_config.sh

#######################################
# Temperature test
# Sometimes run_bram_analysis.sh tried to read temperature from tmux
#   before it was displayed by vivado
#######################################

# Verify content of temperature files
while IFS= read -r line || [[ -n "$line" ]]; do
    if [ ${#line} -gt 9 ] || [[ ! $line =~ ^[0-9\.[:space:]]+$ ]]; then
        echo $line
        echo "Temperature test failed"
        exit 0
    fi
done < "tests/temp_dir/boards/te0802/pblock_1/RAMB36_X2Y12/previous_value_ff_t=0/temperature.txt"

while IFS= read -r line || [[ -n "$line" ]]; do
    if [ ${#line} -gt 9 ] || [[ ! $line =~ ^[0-9\.[:space:]]+$ ]]; then
        echo $line
        echo "Temperature test failed"
        exit 0
    fi
done < "tests/temp_dir/boards/te0802/pblock_1/RAMB36_X2Y12/previous_value_00_t=0/temperature.txt"


#######################################
# Bitstream Copy Test
# In a previous version bitstreams of the last bram block
# were always copied to the next directory,
# instead of copying newly generated bitstreams
# Here we verify against this case
#######################################
first_bram_y=12
second_bram_y=13
base_path=tests/temp_dir/boards/te0802/pblock_1/

bitstreams=(
  RAMB36_X2Y@/bs/RAMB36_X2Y@_00.bit
  RAMB36_X2Y@/bs/RAMB36_X2Y@_bramless_partial.bit
  RAMB36_X2Y@/bs/RAMB36_X2Y@_ff.bit
  RAMB36_X2Y@/bs/RAMB36_X2Y@_modified_partial.bin
  RAMB36_X2Y@/bs/RAMB36_X2Y@_partial_bram_bs.bit
)

for bitstream in "${bitstreams[@]}";
do
  bit_name1="${base_path}${bitstream//@/$first_bram_y}"
  bit_name2="${base_path}${bitstream//@/$second_bram_y}"

  hash_1=($(sha256sum $bit_name1))
  hash_2=($(sha256sum $bit_name2))

  if [[ "${hash_1}" == "${hash_2}" ]]; then
    echo "Error bitstream was copied to next bram block dir";
    exit 0
  fi
done

echo "Tests succeeded"
