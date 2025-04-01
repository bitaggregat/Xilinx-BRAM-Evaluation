# Script is supposed to be used with vivado
# Flashes bitstream from path (arg 1) to device (arg 0)

# Open fpga via hardware manager
open_hw_manager
connect_hw_server
current_hw_target [lindex $argv 0]
open_hw_target

set_property PROGRAM.FILE [lindex $argv 1] [current_hw_device]
program_hw_devices [current_hw_device]
