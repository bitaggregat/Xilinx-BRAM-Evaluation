#!/usr/bin/env bash

bram_idxs=("Y6" "Y7" "Y8")
previous_values=("ff" "00")

for idx in "${bram_idxs[@]}"; do
    for prev_val in "${previous_values[@]}"; do
        echo Hit reset and enable switch on basys3 board then press enter to continue...
        read

        python initialize_bram.py -nb "bitstreams/pblock3/return_0_partial.bit" -fb "bitstreams/pblock3/read_BRAM_X30Y35_RAMB_X1${idx}_${prev_val}_full.bit" -pb "bitstreams/pblock3/read_BRAM_X30Y35_RAMB_X1${idx}_ff_partial.bit"
        
        python reading/read_bram_ftdi.py -v "${prev_val}"
    done
    
done


