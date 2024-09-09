
open_hw_manager
connect_hw_server
current_hw_target [lindex $argv 0]
open_hw_target

# Flash full bitstream
set_property PROGRAM.FILE [lindex $argv 1] [current_hw_device]
program_hw_devices [current_hw_device]

# Flash bramless partial bitstream
set_property PROGRAM.FILE [lindex $argv 2] [current_hw_device]
program_hw_devices -skip_reset [current_hw_device] 

# Flash modified partial bitstream
set_property PROGRAM.FILE [lindex $argv 3] [current_hw_device]
program_hw_devices -skip_reset [current_hw_device] 

close_hw_target
close_hw_manager