# Open fpga via hardware manager
open_hw_manager
connect_hw_server
current_hw_target [lindex $argv 0]
set_property PARAM.FREQUENCY 30000000 [lindex $argv 0]
open_hw_target