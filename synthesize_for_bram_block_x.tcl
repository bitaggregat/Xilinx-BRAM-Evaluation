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
    set_property PROHIBIT true [get_sites [format "RAMB36_X%sY%s" $x_pos $i]]
}
# Then unprohibit bram 18 block of index $bram_y_index
set_property PROHIBIT false [get_sites [format "RAMB36_X%sY%s" $x_pos $bram_y_index]]

save_constraints

# run synthesis
reset_run synth_1
launch_runs synth_1 -jobs 8
wait_on_run synth_1
# run implementation and generate bitstreams
launch_runs impl_1 child_0_impl_1 child_1_impl_1 child_2_impl_1 -jobs 8
wait_on_run impl_1 child_0_impl_1 child_1_impl_1 child_2_impl_1
# generate bitstreams
launch_runs impl_1 child_0_impl_1 child_1_impl_1 child_2_impl_1 -to_step write_bitstream -jobs 8