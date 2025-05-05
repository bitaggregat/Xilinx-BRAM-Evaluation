# Parse arguments:
if { $argc != 6 } {
    puts stderr "Wrong Number of arguments. 5 Arguments needed."
}
set project_xpr [lindex $argv 0]
set pblock [lindex $argv 1]
set x_pos [lindex $argv 2]
set y_min_pos [lindex $argv 3]
set y_max_pos [lindex $argv 4]
set bram_y_index [lindex $argv 5]

# Print all arguments for verification
puts [format "Pblock: %s" $pblock]
puts [format "X Position: %s" $x_pos]
puts [format "BRAM Block Range: RAMB36_X%sY%s:RAMB36_X%sY%s" $x_pos $y_min_pos $x_pos $y_max_pos]
puts [format "Bram Block location: RAMB36_X%sY%s" $x_pos $bram_y_index]


# Open Vivado project
open_project $project_xpr
update_compile_order -fileset sources_1
open_run synth_1 -name synth_1 -pr_config [current_pr_configuration]


# Assign partial design to pblock
add_cells_to_pblock [get_pblocks $pblock] [get_cells -quiet [list bram_wrap]]
# Prohibit all bram blocks for given row $x

for {set i $y_min_pos} {$i <= $y_max_pos} {incr i} {
    puts [format "prohibit RAMB36_X%sY%s" $x_pos $i]
    set_property PROHIBIT true [get_sites [format "RAMB36_X%sY%s" $x_pos $i]]
}
# Then unprohibit bram 36 block of index $bram_y_index
set_property PROHIBIT false [get_sites [format "RAMB36_X%sY%s" $x_pos $bram_y_index]]

save_constraints

# run synthesis
reset_run synth_1
launch_runs synth_1 -jobs 8
wait_on_run synth_1

# run implementation and generate bitstreams
launch_runs impl_1 child_0_impl_1 child_1_impl_1 child_2_impl_1 -jobs 8 -to_step route_design
wait_on_run impl_1 child_0_impl_1 child_1_impl_1 child_2_impl_1

# generate bitstreams


set_property BITSTREAM.GENERAL.COMPRESS FALSE [current_design]
# Uncompressed partial bitstream with value ff
# child_1_impl_1/bram_wrap_bram_wrap_ff_partial.bit
set run_directory [get_property DIRECTORY [get_runs child_1_impl_1]]
open_run child_1_impl_1
write_bitstream -force $run_directory/bram_wrap_bram_wrap_ff.bit
wait_on_run child_1_impl_1

# Write other Bitstreams as compressed

# child_1_impl_1/read_bram.bit (full bs ff)
set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]
write_bitstream -force $run_directory/read_bram.bit
wait_on_run child_1_impl_1

# /child_0_impl_1/read_bram.bit (full bs 00)
set run_directory [get_property DIRECTORY [get_runs child_0_impl_1]]
open_run child_0_impl_1
set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]
write_bitstream -force $run_directory/read_bram.bit
wait_on_run child_0_impl_1

# child_2_impl_1/bram_wrap_return_0_partial.bit (nop bram bs)
set run_directory [get_property DIRECTORY [get_runs child_2_impl_1]]
open_run child_2_impl_1
set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]
write_bitstream -force $run_directory/bram_wrap_return_0.bit
wait_on_run child_2_impl_1
