#set_property PACKAGE_PIN P3 [get_ports rst]
#set_property IOSTANDARD LVCMOS18 [get_ports rst]

#set_property IOSTANDARD LVCMOS18 [get_ports test_switch]
#set_property PACKAGE_PIN P2 [get_ports test_switch]

set_property PACKAGE_PIN F7 [get_ports uart_tx_o]
set_property IOSTANDARD LVCMOS18 [get_ports uart_tx_o]
set_property PACKAGE_PIN E6 [get_ports uart_rx_i]
set_property IOSTANDARD LVCMOS18 [get_ports uart_rx_i]
set_property IOSTANDARD LVCMOS18 [get_ports clk_i]
set_property PACKAGE_PIN J3 [get_ports clk_i]
#set_property IOSTANDARD LVCMOS18 [get_ports maxihpm0_lpd_aclk]
#set_property PACKAGE_PIN U15 [get_ports maxihpm0_lpd_aclk]

set_property IOSTANDARD LVCMOS18 [get_ports {led_o[7]}]
set_property IOSTANDARD LVCMOS18 [get_ports {led_o[6]}]
set_property IOSTANDARD LVCMOS18 [get_ports {led_o[5]}]
set_property IOSTANDARD LVCMOS18 [get_ports {led_o[4]}]
set_property IOSTANDARD LVCMOS18 [get_ports {led_o[3]}]
set_property IOSTANDARD LVCMOS18 [get_ports {led_o[2]}]
set_property IOSTANDARD LVCMOS18 [get_ports {led_o[1]}]
set_property IOSTANDARD LVCMOS18 [get_ports {led_o[0]}]

set_property PACKAGE_PIN L3 [get_ports {led_o[7]}]
set_property PACKAGE_PIN L4 [get_ports {led_o[6]}]
set_property PACKAGE_PIN H2 [get_ports {led_o[5]}]
set_property PACKAGE_PIN J1 [get_ports {led_o[4]}]
set_property PACKAGE_PIN L2 [get_ports {led_o[3]}]
set_property PACKAGE_PIN M2 [get_ports {led_o[2]}]
set_property PACKAGE_PIN N2 [get_ports {led_o[1]}]
set_property PACKAGE_PIN P1 [get_ports {led_o[0]}]




#set_property PROHIBIT true [get_bels RAMB36_X1Y7/RAMBFIFO36E1]
#set_property PROHIBIT true [get_bels RAMB36_X1Y8/RAMBFIFO36E1]


#add_cells_to_pblock [get_pblocks pblock_1] [get_cells -quiet [list bram_wrap]]
#resize_pblock [get_pblocks pblock_1] -add {SLICE_X40Y0:SLICE_X49Y49}
#resize_pblock [get_pblocks pblock_1] -add {RAMB18_X1Y0:RAMB18_X1Y19}
#resize_pblock [get_pblocks pblock_1] -add {RAMB36_X1Y0:RAMB36_X1Y9}


create_pblock pblock_1
add_cells_to_pblock [get_pblocks pblock_1] [get_cells -quiet [list bram_wrap]]
resize_pblock [get_pblocks pblock_1] -add {SLICE_X22Y60:SLICE_X24Y119}
resize_pblock [get_pblocks pblock_1] -add {RAMB18_X2Y24:RAMB18_X2Y47}
resize_pblock [get_pblocks pblock_1] -add {RAMB36_X2Y12:RAMB36_X2Y23}
set_property SNAPPING_MODE ON [get_pblocks pblock_1]

#set_property PROHIBIT true [get_bels RAMB36_X2Y14/RAMBFIFO36E2]

set_property PROHIBIT true [get_sites SLICE_X22Y60]
set_property PROHIBIT true [get_sites SLICE_X23Y60]
set_property PROHIBIT true [get_sites SLICE_X24Y60]
create_pblock pblock_2
resize_pblock [get_pblocks pblock_2] -add {SLICE_X11Y60:SLICE_X13Y119}
resize_pblock [get_pblocks pblock_2] -add {RAMB18_X1Y24:RAMB18_X1Y47}
resize_pblock [get_pblocks pblock_2] -add {RAMB36_X1Y12:RAMB36_X1Y23}
set_property SNAPPING_MODE ON [get_pblocks pblock_2]






































































create_pblock pblock_3
resize_pblock [get_pblocks pblock_3] -add {SLICE_X1Y60:SLICE_X3Y119}
resize_pblock [get_pblocks pblock_3] -add {RAMB18_X0Y24:RAMB18_X0Y47}
resize_pblock [get_pblocks pblock_3] -add {RAMB36_X0Y12:RAMB36_X0Y23}
set_property SNAPPING_MODE ON [get_pblocks pblock_3]
create_pblock pblock_4
resize_pblock [get_pblocks pblock_4] -add {SLICE_X22Y0:SLICE_X24Y59}
resize_pblock [get_pblocks pblock_4] -add {RAMB18_X2Y0:RAMB18_X2Y23}
resize_pblock [get_pblocks pblock_4] -add {RAMB36_X2Y0:RAMB36_X2Y11}
set_property SNAPPING_MODE ON [get_pblocks pblock_4]
create_pblock pblock_5
resize_pblock [get_pblocks pblock_5] -add {SLICE_X11Y0:SLICE_X13Y59}
resize_pblock [get_pblocks pblock_5] -add {RAMB18_X1Y0:RAMB18_X1Y23}
resize_pblock [get_pblocks pblock_5] -add {RAMB36_X1Y0:RAMB36_X1Y11}
set_property SNAPPING_MODE ON [get_pblocks pblock_5]
create_pblock pblock_6
resize_pblock [get_pblocks pblock_6] -add {SLICE_X1Y0:SLICE_X3Y59}
resize_pblock [get_pblocks pblock_6] -add {RAMB18_X0Y0:RAMB18_X0Y23}
resize_pblock [get_pblocks pblock_6] -add {RAMB36_X0Y0:RAMB36_X0Y11}
set_property SNAPPING_MODE ON [get_pblocks pblock_6]
create_pblock pblock_7
resize_pblock [get_pblocks pblock_7] -add {SLICE_X0Y120:SLICE_X4Y179}
resize_pblock [get_pblocks pblock_7] -add {RAMB18_X0Y48:RAMB18_X0Y71}
resize_pblock [get_pblocks pblock_7] -add {RAMB36_X0Y24:RAMB36_X0Y35}
set_property SNAPPING_MODE ON [get_pblocks pblock_7]
create_pblock pblock_8
resize_pblock [get_pblocks pblock_8] -add {SLICE_X8Y120:SLICE_X14Y179}
resize_pblock [get_pblocks pblock_8] -add {RAMB18_X1Y48:RAMB18_X1Y71}
resize_pblock [get_pblocks pblock_8] -add {RAMB36_X1Y24:RAMB36_X1Y35}
set_property SNAPPING_MODE ON [get_pblocks pblock_8]
create_pblock pblock_9
resize_pblock [get_pblocks pblock_9] -add {SLICE_X22Y120:SLICE_X24Y179}
resize_pblock [get_pblocks pblock_9] -add {RAMB18_X2Y48:RAMB18_X2Y71}
resize_pblock [get_pblocks pblock_9] -add {RAMB36_X2Y24:RAMB36_X2Y35}
set_property SNAPPING_MODE ON [get_pblocks pblock_9]

set_property PROHIBIT true [get_sites SLICE_X1Y120]
set_property PROHIBIT true [get_sites SLICE_X2Y120]
set_property PROHIBIT true [get_sites SLICE_X3Y120]

set_property PROHIBIT true [get_sites SLICE_X22Y59]
set_property PROHIBIT true [get_sites SLICE_X23Y59]
set_property PROHIBIT true [get_sites SLICE_X24Y59]









































































set_property PROHIBIT true [get_sites SLICE_X22Y120]
set_property PROHIBIT true [get_sites SLICE_X23Y120]
set_property PROHIBIT true [get_sites SLICE_X24Y120]

set_property PROHIBIT true [get_sites SLICE_X11Y120]
set_property PROHIBIT true [get_sites SLICE_X12Y120]
set_property PROHIBIT true [get_sites SLICE_X13Y120]







set_property PROHIBIT true [get_sites SLICE_X9Y120]
set_property PROHIBIT true [get_sites SLICE_X10Y120]






















































































set_property PROHIBIT true [get_sites RAMB36_X1Y24]


set_property PROHIBIT true [get_sites RAMB36_X1Y26]

set_property PROHIBIT true [get_sites RAMB36_X1Y27]

set_property PROHIBIT true [get_sites RAMB36_X1Y28]

set_property PROHIBIT true [get_sites RAMB36_X1Y29]

set_property PROHIBIT true [get_sites RAMB36_X1Y30]

set_property PROHIBIT true [get_sites RAMB36_X1Y31]

set_property PROHIBIT true [get_sites RAMB36_X1Y32]

set_property PROHIBIT true [get_sites RAMB36_X1Y33]

set_property PROHIBIT true [get_sites RAMB36_X1Y34]


















set_property PROHIBIT true [get_sites RAMB36_X2Y13]

set_property PROHIBIT true [get_sites RAMB36_X2Y14]

set_property PROHIBIT true [get_sites RAMB36_X2Y15]

set_property PROHIBIT true [get_sites RAMB36_X2Y16]

set_property PROHIBIT true [get_sites RAMB36_X2Y17]

set_property PROHIBIT true [get_sites RAMB36_X2Y18]

set_property PROHIBIT true [get_sites RAMB36_X2Y19]

set_property PROHIBIT true [get_sites RAMB36_X2Y20]

set_property PROHIBIT true [get_sites RAMB36_X2Y21]




set_property PROHIBIT true [get_sites RAMB36_X1Y13]

set_property PROHIBIT true [get_sites RAMB36_X1Y14]

set_property PROHIBIT true [get_sites RAMB36_X1Y15]

set_property PROHIBIT true [get_sites RAMB36_X1Y16]

set_property PROHIBIT true [get_sites RAMB36_X1Y17]

set_property PROHIBIT true [get_sites RAMB36_X1Y18]

set_property PROHIBIT true [get_sites RAMB36_X1Y19]

set_property PROHIBIT true [get_sites RAMB36_X1Y20]

set_property PROHIBIT true [get_sites RAMB36_X1Y21]

set_property PROHIBIT true [get_sites RAMB36_X1Y22]


set_property PROHIBIT true [get_sites RAMB36_X0Y12]

set_property PROHIBIT true [get_sites RAMB36_X0Y13]

set_property PROHIBIT true [get_sites RAMB36_X0Y14]

set_property PROHIBIT true [get_sites RAMB36_X0Y15]

set_property PROHIBIT true [get_sites RAMB36_X0Y16]

set_property PROHIBIT true [get_sites RAMB36_X0Y17]

set_property PROHIBIT true [get_sites RAMB36_X0Y18]

set_property PROHIBIT true [get_sites RAMB36_X0Y19]

set_property PROHIBIT true [get_sites RAMB36_X0Y20]

set_property PROHIBIT true [get_sites RAMB36_X0Y21]

set_property PROHIBIT true [get_sites RAMB36_X0Y22]


set_property PROHIBIT true [get_sites RAMB36_X2Y0]

set_property PROHIBIT true [get_sites RAMB36_X2Y1]

set_property PROHIBIT true [get_sites RAMB36_X2Y2]

set_property PROHIBIT true [get_sites RAMB36_X2Y3]

set_property PROHIBIT true [get_sites RAMB36_X2Y4]

set_property PROHIBIT true [get_sites RAMB36_X2Y5]

set_property PROHIBIT true [get_sites RAMB36_X2Y6]

set_property PROHIBIT true [get_sites RAMB36_X2Y7]

set_property PROHIBIT true [get_sites RAMB36_X2Y8]

set_property PROHIBIT true [get_sites RAMB36_X2Y9]

set_property PROHIBIT true [get_sites RAMB36_X2Y10]


set_property PROHIBIT true [get_sites RAMB36_X1Y0]

set_property PROHIBIT true [get_sites RAMB36_X1Y1]

set_property PROHIBIT true [get_sites RAMB36_X1Y2]

set_property PROHIBIT true [get_sites RAMB36_X1Y3]

set_property PROHIBIT true [get_sites RAMB36_X1Y4]

set_property PROHIBIT true [get_sites RAMB36_X1Y5]

set_property PROHIBIT true [get_sites RAMB36_X1Y6]

set_property PROHIBIT true [get_sites RAMB36_X1Y7]

set_property PROHIBIT true [get_sites RAMB36_X1Y8]

set_property PROHIBIT true [get_sites RAMB36_X1Y9]

set_property PROHIBIT true [get_sites RAMB36_X1Y10]


set_property PROHIBIT true [get_sites RAMB36_X0Y0]

set_property PROHIBIT true [get_sites RAMB36_X0Y1]

set_property PROHIBIT true [get_sites RAMB36_X0Y2]

set_property PROHIBIT true [get_sites RAMB36_X0Y3]

set_property PROHIBIT true [get_sites RAMB36_X0Y4]

set_property PROHIBIT true [get_sites RAMB36_X0Y5]

set_property PROHIBIT true [get_sites RAMB36_X0Y6]

set_property PROHIBIT true [get_sites RAMB36_X0Y7]

set_property PROHIBIT true [get_sites RAMB36_X0Y8]

set_property PROHIBIT true [get_sites RAMB36_X0Y9]

set_property PROHIBIT true [get_sites RAMB36_X0Y10]


set_property PROHIBIT true [get_sites RAMB36_X0Y24]

set_property PROHIBIT true [get_sites RAMB36_X0Y25]

set_property PROHIBIT true [get_sites RAMB36_X0Y26]

set_property PROHIBIT true [get_sites RAMB36_X0Y27]

set_property PROHIBIT true [get_sites RAMB36_X0Y28]

set_property PROHIBIT true [get_sites RAMB36_X0Y29]

set_property PROHIBIT true [get_sites RAMB36_X0Y30]

set_property PROHIBIT true [get_sites RAMB36_X0Y31]

set_property PROHIBIT true [get_sites RAMB36_X0Y32]

set_property PROHIBIT true [get_sites RAMB36_X0Y33]

set_property PROHIBIT true [get_sites RAMB36_X0Y34]



set_property PROHIBIT true [get_sites RAMB36_X2Y24]

set_property PROHIBIT true [get_sites RAMB36_X2Y25]

set_property PROHIBIT true [get_sites RAMB36_X2Y26]

set_property PROHIBIT true [get_sites RAMB36_X2Y27]

set_property PROHIBIT true [get_sites RAMB36_X2Y28]

set_property PROHIBIT true [get_sites RAMB36_X2Y29]

set_property PROHIBIT true [get_sites RAMB36_X2Y30]

set_property PROHIBIT true [get_sites RAMB36_X2Y31]

set_property PROHIBIT true [get_sites RAMB36_X2Y32]

set_property PROHIBIT true [get_sites RAMB36_X2Y33]

set_property PROHIBIT true [get_sites RAMB36_X2Y34]

set_property PROHIBIT true [get_sites RAMB36_X1Y23]


set_property PROHIBIT true [get_sites SLICE_X22Y119]
set_property PROHIBIT true [get_sites SLICE_X23Y119]
set_property PROHIBIT true [get_sites SLICE_X24Y119]
set_property LOCK_PINS {I0:A1 I1:A2 I2:A3 I3:A4 I4:A6 I5:A5} [get_cells {tx/tx_data[5]_i_2}]
set_property LOCK_PINS {I0:A1 I1:A2 I2:A3 I3:A4 I4:A6 I5:A5} [get_cells {tx/tx_data[0]_i_2}]
set_property LOCK_PINS {I0:A1 I1:A2 I2:A3 I3:A4 I4:A6 I5:A5} [get_cells {tx/tx_data[1]_i_2}]
set_property LOCK_PINS {I0:A1 I1:A2 I2:A3 I3:A4 I4:A6 I5:A5} [get_cells {tx/tx_data[2]_i_2}]
set_property LOCK_PINS {I0:A1 I1:A2 I2:A3 I3:A4 I4:A6 I5:A5} [get_cells {tx/tx_data[3]_i_2}]
set_property LOCK_PINS {I0:A1 I1:A2 I2:A3 I3:A4 I4:A6 I5:A5} [get_cells {tx/tx_data[4]_i_2}]
set_property LOCK_PINS {I0:A1 I1:A2 I2:A3 I3:A4 I4:A6 I5:A5} [get_cells {tx/tx_data[6]_i_2}]
set_property LOCK_PINS {I0:A1 I1:A2 I2:A3 I3:A4 I4:A6 I5:A5} [get_cells {tx/tx_data[7]_i_5}]
set_property PROHIBIT true [get_sites RAMB18_X2Y46]
set_property PROHIBIT true [get_sites RAMB18_X2Y43]
set_property PROHIBIT true [get_sites RAMB18_X2Y42]
set_property PROHIBIT true [get_sites RAMB18_X2Y41]
set_property PROHIBIT true [get_sites RAMB18_X2Y40]
set_property PROHIBIT true [get_sites RAMB18_X2Y39]
set_property PROHIBIT true [get_sites RAMB18_X2Y38]
set_property PROHIBIT true [get_sites RAMB18_X2Y37]
set_property PROHIBIT true [get_sites RAMB18_X2Y36]
set_property PROHIBIT true [get_sites RAMB18_X2Y35]
set_property PROHIBIT true [get_sites RAMB18_X2Y34]
set_property PROHIBIT true [get_sites RAMB18_X2Y33]
set_property PROHIBIT true [get_sites RAMB18_X2Y32]
set_property PROHIBIT true [get_sites RAMB18_X2Y31]
set_property PROHIBIT true [get_sites RAMB18_X2Y30]
set_property PROHIBIT true [get_sites RAMB18_X2Y29]
set_property PROHIBIT true [get_sites RAMB18_X2Y28]
set_property PROHIBIT true [get_sites RAMB18_X2Y27]
set_property PROHIBIT true [get_sites RAMB18_X2Y26]
set_property PROHIBIT true [get_sites RAMB36_X2Y23]
set_property PROHIBIT true [get_sites RAMB18_X2Y47]
set_property PROHIBIT true [get_sites RAMB18_X2Y24]
set_property PROHIBIT true [get_sites RAMB36_X2Y12]
set_property PROHIBIT true [get_sites RAMB18_X2Y25]
