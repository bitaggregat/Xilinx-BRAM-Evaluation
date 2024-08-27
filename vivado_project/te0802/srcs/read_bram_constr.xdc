set_property PACKAGE_PIN P3 [get_ports rst]
set_property IOSTANDARD LVCMOS18 [get_ports rst]

set_property PACKAGE_PIN F7 [get_ports uart_txd]
set_property IOSTANDARD LVCMOS18 [get_ports uart_txd]
set_property IOSTANDARD LVCMOS18 [get_ports sys_clk_p]
set_property PACKAGE_PIN J3 [get_ports sys_clk_p]
#set_property IOSTANDARD LVCMOS18 [get_ports maxihpm0_lpd_aclk]
#set_property PACKAGE_PIN U15 [get_ports maxihpm0_lpd_aclk]

set_property IOSTANDARD LVCMOS18 [get_ports {led[7]}]
set_property IOSTANDARD LVCMOS18 [get_ports {led[6]}]
set_property IOSTANDARD LVCMOS18 [get_ports {led[5]}]
set_property IOSTANDARD LVCMOS18 [get_ports {led[4]}]
set_property IOSTANDARD LVCMOS18 [get_ports {led[3]}]
set_property IOSTANDARD LVCMOS18 [get_ports {led[2]}]
set_property IOSTANDARD LVCMOS18 [get_ports {led[1]}]
set_property IOSTANDARD LVCMOS18 [get_ports {led[0]}]

set_property PACKAGE_PIN L3 [get_ports {led[7]}]
set_property PACKAGE_PIN L4 [get_ports {led[6]}]
set_property PACKAGE_PIN H2 [get_ports {led[5]}]
set_property PACKAGE_PIN J1 [get_ports {led[4]}]
set_property PACKAGE_PIN L2 [get_ports {led[3]}]
set_property PACKAGE_PIN M2 [get_ports {led[2]}]
set_property PACKAGE_PIN N2 [get_ports {led[1]}]
set_property PACKAGE_PIN P1 [get_ports {led[0]}]

set_property IOSTANDARD LVCMOS18 [get_ports send_enable]
set_property PACKAGE_PIN P2 [get_ports send_enable]


#set_property PROHIBIT true [get_bels RAMB36_X1Y7/RAMBFIFO36E1]
#set_property PROHIBIT true [get_bels RAMB36_X1Y8/RAMBFIFO36E1]


#add_cells_to_pblock [get_pblocks pblock_1] [get_cells -quiet [list bram_wrap]]
#resize_pblock [get_pblocks pblock_1] -add {SLICE_X40Y0:SLICE_X49Y49}
#resize_pblock [get_pblocks pblock_1] -add {RAMB18_X1Y0:RAMB18_X1Y19}
#resize_pblock [get_pblocks pblock_1] -add {RAMB36_X1Y0:RAMB36_X1Y9}


create_pblock pblock_1
resize_pblock [get_pblocks pblock_1] -add {SLICE_X22Y60:SLICE_X24Y89}
resize_pblock [get_pblocks pblock_1] -add {RAMB18_X2Y24:RAMB18_X2Y35}
resize_pblock [get_pblocks pblock_1] -add {RAMB36_X2Y12:RAMB36_X2Y17}
set_property SNAPPING_MODE ON [get_pblocks pblock_1]

#set_property PROHIBIT true [get_bels RAMB36_X2Y14/RAMBFIFO36E2]

set_property PROHIBIT true [get_sites SLICE_X22Y60]
set_property PROHIBIT true [get_sites SLICE_X23Y60]
set_property PROHIBIT true [get_sites SLICE_X24Y60]
create_pblock pblock_2
add_cells_to_pblock [get_pblocks pblock_2] [get_cells -quiet [list bram_wrap]]
resize_pblock [get_pblocks pblock_2] -add {SLICE_X11Y60:SLICE_X13Y89}
resize_pblock [get_pblocks pblock_2] -add {RAMB18_X1Y24:RAMB18_X1Y35}
resize_pblock [get_pblocks pblock_2] -add {RAMB36_X1Y12:RAMB36_X1Y17}
set_property SNAPPING_MODE ON [get_pblocks pblock_2]


set_property PROHIBIT true [get_sites RAMB36_X1Y14]
set_property PROHIBIT true [get_sites RAMB36_X1Y15]
set_property PROHIBIT true [get_sites RAMB36_X1Y16]
set_property PROHIBIT true [get_sites RAMB36_X1Y17]

set_property PROHIBIT true [get_sites RAMB36_X1Y13]

