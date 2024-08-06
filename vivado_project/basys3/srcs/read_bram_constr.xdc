set_property PACKAGE_PIN R2 [get_ports rst]
set_property IOSTANDARD LVCMOS33 [get_ports rst]

set_property PACKAGE_PIN A18 [get_ports uart_txd]
set_property IOSTANDARD LVCMOS33 [get_ports uart_txd]
set_property IOSTANDARD LVCMOS33 [get_ports sys_clk_p]
set_property PACKAGE_PIN W5 [get_ports sys_clk_p]

set_property IOSTANDARD LVCMOS33 [get_ports {led[7]}]
set_property IOSTANDARD LVCMOS33 [get_ports {led[6]}]
set_property IOSTANDARD LVCMOS33 [get_ports {led[5]}]
set_property IOSTANDARD LVCMOS33 [get_ports {led[4]}]
set_property IOSTANDARD LVCMOS33 [get_ports {led[3]}]
set_property IOSTANDARD LVCMOS33 [get_ports {led[2]}]
set_property IOSTANDARD LVCMOS33 [get_ports {led[1]}]
set_property IOSTANDARD LVCMOS33 [get_ports {led[0]}]

set_property PACKAGE_PIN U16 [get_ports {led[7]}]
set_property PACKAGE_PIN E19 [get_ports {led[6]}]
set_property PACKAGE_PIN V19 [get_ports {led[5]}]
set_property PACKAGE_PIN W18 [get_ports {led[4]}]
set_property PACKAGE_PIN U15 [get_ports {led[3]}]
set_property PACKAGE_PIN U14 [get_ports {led[2]}]
set_property PACKAGE_PIN V14 [get_ports {led[1]}]
set_property PACKAGE_PIN V13 [get_ports {led[0]}]

set_property IOSTANDARD LVCMOS33 [get_ports send_enable]
set_property PACKAGE_PIN T1 [get_ports send_enable]


#set_property PROHIBIT true [get_bels RAMB36_X1Y7/RAMBFIFO36E1]
#set_property PROHIBIT true [get_bels RAMB36_X1Y8/RAMBFIFO36E1]


create_pblock pblock_1
add_cells_to_pblock [get_pblocks pblock_1] [get_cells -quiet [list bram_wrap]]
resize_pblock [get_pblocks pblock_1] -add {SLICE_X40Y0:SLICE_X49Y49}
resize_pblock [get_pblocks pblock_1] -add {RAMB18_X1Y0:RAMB18_X1Y19}
resize_pblock [get_pblocks pblock_1] -add {RAMB36_X1Y0:RAMB36_X1Y9}



