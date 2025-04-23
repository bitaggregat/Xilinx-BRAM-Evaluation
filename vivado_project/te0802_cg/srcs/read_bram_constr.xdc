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




create_pblock pblock_1
resize_pblock [get_pblocks pblock_1] -add {SLICE_X44Y0:SLICE_X48Y59}
resize_pblock [get_pblocks pblock_1] -add {RAMB18_X5Y0:RAMB18_X5Y23}
resize_pblock [get_pblocks pblock_1] -add {RAMB36_X5Y0:RAMB36_X5Y11}
set_property SNAPPING_MODE ON [get_pblocks pblock_1]
create_pblock pblock_2
resize_pblock [get_pblocks pblock_2] -add {SLICE_X34Y0:SLICE_X37Y59}
resize_pblock [get_pblocks pblock_2] -add {RAMB18_X4Y0:RAMB18_X4Y23}
resize_pblock [get_pblocks pblock_2] -add {RAMB36_X4Y0:RAMB36_X4Y11}
set_property SNAPPING_MODE ON [get_pblocks pblock_2]
create_pblock pblock_3
resize_pblock [get_pblocks pblock_3] -add {SLICE_X29Y0:SLICE_X33Y59}
resize_pblock [get_pblocks pblock_3] -add {RAMB18_X3Y0:RAMB18_X3Y23}
resize_pblock [get_pblocks pblock_3] -add {RAMB36_X3Y0:RAMB36_X3Y11}
set_property SNAPPING_MODE ON [get_pblocks pblock_3]
create_pblock pblock_4
resize_pblock [get_pblocks pblock_4] -add {SLICE_X15Y0:SLICE_X19Y59}
resize_pblock [get_pblocks pblock_4] -add {RAMB18_X2Y0:RAMB18_X2Y23}
resize_pblock [get_pblocks pblock_4] -add {RAMB36_X2Y0:RAMB36_X2Y11}
set_property SNAPPING_MODE ON [get_pblocks pblock_4]
create_pblock pblock_5
add_cells_to_pblock [get_pblocks pblock_5] [get_cells -quiet [list bram_wrap]]
resize_pblock [get_pblocks pblock_5] -add {SLICE_X6Y0:SLICE_X14Y59}
resize_pblock [get_pblocks pblock_5] -add {RAMB18_X1Y0:RAMB18_X1Y23}
resize_pblock [get_pblocks pblock_5] -add {RAMB36_X1Y0:RAMB36_X1Y11}
set_property SNAPPING_MODE ON [get_pblocks pblock_5]
create_pblock pblock_6
resize_pblock [get_pblocks pblock_6] -add {SLICE_X0Y0:SLICE_X4Y59}
resize_pblock [get_pblocks pblock_6] -add {RAMB18_X0Y0:RAMB18_X0Y23}
resize_pblock [get_pblocks pblock_6] -add {RAMB36_X0Y0:RAMB36_X0Y11}
set_property SNAPPING_MODE ON [get_pblocks pblock_6]
create_pblock pblock_7
resize_pblock [get_pblocks pblock_7] -add {SLICE_X44Y60:SLICE_X48Y119}
resize_pblock [get_pblocks pblock_7] -add {RAMB18_X5Y24:RAMB18_X5Y47}
resize_pblock [get_pblocks pblock_7] -add {RAMB36_X5Y12:RAMB36_X5Y23}
set_property SNAPPING_MODE ON [get_pblocks pblock_7]
create_pblock pblock_8
resize_pblock [get_pblocks pblock_8] -add {SLICE_X34Y60:SLICE_X38Y119}
resize_pblock [get_pblocks pblock_8] -add {RAMB18_X4Y24:RAMB18_X4Y47}
resize_pblock [get_pblocks pblock_8] -add {RAMB36_X4Y12:RAMB36_X4Y23}
set_property SNAPPING_MODE ON [get_pblocks pblock_8]
create_pblock pblock_9
resize_pblock [get_pblocks pblock_9] -add {SLICE_X29Y60:SLICE_X33Y119}
resize_pblock [get_pblocks pblock_9] -add {RAMB18_X3Y24:RAMB18_X3Y47}
resize_pblock [get_pblocks pblock_9] -add {RAMB36_X3Y12:RAMB36_X3Y23}
set_property SNAPPING_MODE ON [get_pblocks pblock_9]
create_pblock pblock_10
resize_pblock [get_pblocks pblock_10] -add {SLICE_X15Y60:SLICE_X20Y119}
resize_pblock [get_pblocks pblock_10] -add {RAMB18_X2Y24:RAMB18_X2Y47}
resize_pblock [get_pblocks pblock_10] -add {RAMB36_X2Y12:RAMB36_X2Y23}
set_property SNAPPING_MODE ON [get_pblocks pblock_10]
create_pblock pblock_11
resize_pblock [get_pblocks pblock_11] -add {SLICE_X10Y60:SLICE_X14Y119}
resize_pblock [get_pblocks pblock_11] -add {RAMB18_X1Y24:RAMB18_X1Y47}
resize_pblock [get_pblocks pblock_11] -add {RAMB36_X1Y12:RAMB36_X1Y23}
set_property SNAPPING_MODE ON [get_pblocks pblock_11]
create_pblock pblock_12
resize_pblock [get_pblocks pblock_12] -add {SLICE_X0Y60:SLICE_X4Y119}
resize_pblock [get_pblocks pblock_12] -add {RAMB18_X0Y24:RAMB18_X0Y47}
resize_pblock [get_pblocks pblock_12] -add {RAMB36_X0Y12:RAMB36_X0Y23}
set_property SNAPPING_MODE ON [get_pblocks pblock_12]
create_pblock pblock_13
resize_pblock [get_pblocks pblock_13] -add {SLICE_X44Y120:SLICE_X48Y179}
resize_pblock [get_pblocks pblock_13] -add {RAMB18_X5Y48:RAMB18_X5Y71}
resize_pblock [get_pblocks pblock_13] -add {RAMB36_X5Y24:RAMB36_X5Y35}
set_property SNAPPING_MODE ON [get_pblocks pblock_13]
create_pblock pblock_14
resize_pblock [get_pblocks pblock_14] -add {SLICE_X34Y120:SLICE_X38Y179}
resize_pblock [get_pblocks pblock_14] -add {RAMB18_X4Y48:RAMB18_X4Y71}
resize_pblock [get_pblocks pblock_14] -add {RAMB36_X4Y24:RAMB36_X4Y35}
set_property SNAPPING_MODE ON [get_pblocks pblock_14]
create_pblock pblock_15
resize_pblock [get_pblocks pblock_15] -add {SLICE_X29Y120:SLICE_X33Y179}
resize_pblock [get_pblocks pblock_15] -add {RAMB18_X3Y48:RAMB18_X3Y71}
resize_pblock [get_pblocks pblock_15] -add {RAMB36_X3Y24:RAMB36_X3Y35}
set_property SNAPPING_MODE ON [get_pblocks pblock_15]
create_pblock pblock_16
resize_pblock [get_pblocks pblock_16] -add {SLICE_X15Y120:SLICE_X19Y179}
resize_pblock [get_pblocks pblock_16] -add {RAMB18_X2Y48:RAMB18_X2Y71}
resize_pblock [get_pblocks pblock_16] -add {RAMB36_X2Y24:RAMB36_X2Y35}
set_property SNAPPING_MODE ON [get_pblocks pblock_16]
create_pblock pblock_17
resize_pblock [get_pblocks pblock_17] -add {SLICE_X6Y120:SLICE_X14Y179}
resize_pblock [get_pblocks pblock_17] -add {RAMB18_X1Y48:RAMB18_X1Y71}
resize_pblock [get_pblocks pblock_17] -add {RAMB36_X1Y24:RAMB36_X1Y35}
set_property SNAPPING_MODE ON [get_pblocks pblock_17]
create_pblock pblock_18
resize_pblock [get_pblocks pblock_18] -add {SLICE_X0Y120:SLICE_X4Y179}
resize_pblock [get_pblocks pblock_18] -add {RAMB18_X0Y48:RAMB18_X0Y71}
resize_pblock [get_pblocks pblock_18] -add {RAMB36_X0Y24:RAMB36_X0Y35}
set_property SNAPPING_MODE ON [get_pblocks pblock_18]


































































































































































































































































































































































































































































































set_property PROHIBIT true [get_sites RAMB36_X2Y12]

set_property PROHIBIT true [get_sites RAMB36_X2Y13]

set_property PROHIBIT true [get_sites RAMB36_X2Y14]

set_property PROHIBIT true [get_sites RAMB36_X2Y15]

set_property PROHIBIT true [get_sites RAMB36_X2Y16]

set_property PROHIBIT true [get_sites RAMB36_X2Y17]

set_property PROHIBIT true [get_sites RAMB36_X2Y18]

set_property PROHIBIT true [get_sites RAMB36_X2Y19]

set_property PROHIBIT true [get_sites RAMB36_X2Y20]

set_property PROHIBIT true [get_sites RAMB36_X2Y21]

set_property PROHIBIT true [get_sites RAMB36_X2Y22]


set_property PROHIBIT true [get_sites RAMB36_X1Y12]

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


set_property PROHIBIT true [get_sites RAMB36_X5Y24]

set_property PROHIBIT true [get_sites RAMB36_X5Y25]

set_property PROHIBIT true [get_sites RAMB36_X5Y26]

set_property PROHIBIT true [get_sites RAMB36_X5Y27]

set_property PROHIBIT true [get_sites RAMB36_X5Y28]

set_property PROHIBIT true [get_sites RAMB36_X5Y29]

set_property PROHIBIT true [get_sites RAMB36_X5Y30]

set_property PROHIBIT true [get_sites RAMB36_X5Y31]

set_property PROHIBIT true [get_sites RAMB36_X5Y32]

set_property PROHIBIT true [get_sites RAMB36_X5Y33]

set_property PROHIBIT true [get_sites RAMB36_X5Y34]


set_property PROHIBIT true [get_sites RAMB36_X4Y24]

set_property PROHIBIT true [get_sites RAMB36_X4Y25]

set_property PROHIBIT true [get_sites RAMB36_X4Y26]

set_property PROHIBIT true [get_sites RAMB36_X4Y27]

set_property PROHIBIT true [get_sites RAMB36_X4Y28]

set_property PROHIBIT true [get_sites RAMB36_X4Y29]

set_property PROHIBIT true [get_sites RAMB36_X4Y30]

set_property PROHIBIT true [get_sites RAMB36_X4Y31]

set_property PROHIBIT true [get_sites RAMB36_X4Y32]

set_property PROHIBIT true [get_sites RAMB36_X4Y33]

set_property PROHIBIT true [get_sites RAMB36_X4Y34]


set_property PROHIBIT true [get_sites RAMB36_X3Y24]

set_property PROHIBIT true [get_sites RAMB36_X3Y25]

set_property PROHIBIT true [get_sites RAMB36_X3Y26]

set_property PROHIBIT true [get_sites RAMB36_X3Y27]

set_property PROHIBIT true [get_sites RAMB36_X3Y28]

set_property PROHIBIT true [get_sites RAMB36_X3Y29]

set_property PROHIBIT true [get_sites RAMB36_X3Y30]

set_property PROHIBIT true [get_sites RAMB36_X3Y31]

set_property PROHIBIT true [get_sites RAMB36_X3Y32]

set_property PROHIBIT true [get_sites RAMB36_X3Y33]

set_property PROHIBIT true [get_sites RAMB36_X3Y34]


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


set_property PROHIBIT true [get_sites RAMB36_X1Y24]

set_property PROHIBIT true [get_sites RAMB36_X1Y25]

set_property PROHIBIT true [get_sites RAMB36_X1Y26]


set_property PROHIBIT true [get_sites RAMB36_X1Y28]

set_property PROHIBIT true [get_sites RAMB36_X1Y29]

set_property PROHIBIT true [get_sites RAMB36_X1Y30]

set_property PROHIBIT true [get_sites RAMB36_X1Y31]

set_property PROHIBIT true [get_sites RAMB36_X1Y32]

set_property PROHIBIT true [get_sites RAMB36_X1Y33]

set_property PROHIBIT true [get_sites RAMB36_X1Y34]


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


set_property PROHIBIT true [get_sites RAMB36_X5Y0]

set_property PROHIBIT true [get_sites RAMB36_X5Y1]

set_property PROHIBIT true [get_sites RAMB36_X5Y2]

set_property PROHIBIT true [get_sites RAMB36_X5Y3]

set_property PROHIBIT true [get_sites RAMB36_X5Y4]

set_property PROHIBIT true [get_sites RAMB36_X5Y5]

set_property PROHIBIT true [get_sites RAMB36_X5Y6]

set_property PROHIBIT true [get_sites RAMB36_X5Y7]

set_property PROHIBIT true [get_sites RAMB36_X5Y8]

set_property PROHIBIT true [get_sites RAMB36_X5Y9]

set_property PROHIBIT true [get_sites RAMB36_X5Y10]


set_property PROHIBIT true [get_sites RAMB36_X4Y0]

set_property PROHIBIT true [get_sites RAMB36_X4Y1]

set_property PROHIBIT true [get_sites RAMB36_X4Y2]

set_property PROHIBIT true [get_sites RAMB36_X4Y3]

set_property PROHIBIT true [get_sites RAMB36_X4Y4]

set_property PROHIBIT true [get_sites RAMB36_X4Y5]

set_property PROHIBIT true [get_sites RAMB36_X4Y6]

set_property PROHIBIT true [get_sites RAMB36_X4Y7]

set_property PROHIBIT true [get_sites RAMB36_X4Y8]

set_property PROHIBIT true [get_sites RAMB36_X4Y9]

set_property PROHIBIT true [get_sites RAMB36_X4Y10]


set_property PROHIBIT true [get_sites RAMB36_X3Y0]

set_property PROHIBIT true [get_sites RAMB36_X3Y1]

set_property PROHIBIT true [get_sites RAMB36_X3Y2]

set_property PROHIBIT true [get_sites RAMB36_X3Y3]

set_property PROHIBIT true [get_sites RAMB36_X3Y4]

set_property PROHIBIT true [get_sites RAMB36_X3Y5]

set_property PROHIBIT true [get_sites RAMB36_X3Y6]

set_property PROHIBIT true [get_sites RAMB36_X3Y7]

set_property PROHIBIT true [get_sites RAMB36_X3Y8]

set_property PROHIBIT true [get_sites RAMB36_X3Y9]

set_property PROHIBIT true [get_sites RAMB36_X3Y10]


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


set_property PROHIBIT true [get_sites RAMB36_X5Y12]

set_property PROHIBIT true [get_sites RAMB36_X5Y13]

set_property PROHIBIT true [get_sites RAMB36_X5Y14]

set_property PROHIBIT true [get_sites RAMB36_X5Y15]

set_property PROHIBIT true [get_sites RAMB36_X5Y16]

set_property PROHIBIT true [get_sites RAMB36_X5Y17]

set_property PROHIBIT true [get_sites RAMB36_X5Y18]

set_property PROHIBIT true [get_sites RAMB36_X5Y19]

set_property PROHIBIT true [get_sites RAMB36_X5Y20]

set_property PROHIBIT true [get_sites RAMB36_X5Y21]

set_property PROHIBIT true [get_sites RAMB36_X5Y22]


set_property PROHIBIT true [get_sites RAMB36_X4Y12]

set_property PROHIBIT true [get_sites RAMB36_X4Y13]

set_property PROHIBIT true [get_sites RAMB36_X4Y14]

set_property PROHIBIT true [get_sites RAMB36_X4Y15]

set_property PROHIBIT true [get_sites RAMB36_X4Y16]

set_property PROHIBIT true [get_sites RAMB36_X4Y17]

set_property PROHIBIT true [get_sites RAMB36_X4Y18]

set_property PROHIBIT true [get_sites RAMB36_X4Y19]

set_property PROHIBIT true [get_sites RAMB36_X4Y20]

set_property PROHIBIT true [get_sites RAMB36_X4Y21]

set_property PROHIBIT true [get_sites RAMB36_X4Y22]


set_property PROHIBIT true [get_sites RAMB36_X3Y12]

set_property PROHIBIT true [get_sites RAMB36_X3Y13]

set_property PROHIBIT true [get_sites RAMB36_X3Y14]

set_property PROHIBIT true [get_sites RAMB36_X3Y15]

set_property PROHIBIT true [get_sites RAMB36_X3Y16]

set_property PROHIBIT true [get_sites RAMB36_X3Y17]

set_property PROHIBIT true [get_sites RAMB36_X3Y18]

set_property PROHIBIT true [get_sites RAMB36_X3Y19]

set_property PROHIBIT true [get_sites RAMB36_X3Y20]

set_property PROHIBIT true [get_sites RAMB36_X3Y21]

set_property PROHIBIT true [get_sites RAMB36_X3Y22]

set_property PROHIBIT true [get_sites SLICE_X29Y119]
set_property PROHIBIT true [get_sites SLICE_X30Y119]
set_property PROHIBIT true [get_sites SLICE_X31Y119]
set_property PROHIBIT true [get_sites SLICE_X32Y119]
set_property PROHIBIT true [get_sites SLICE_X33Y119]
set_property PROHIBIT true [get_sites SLICE_X29Y60]
set_property PROHIBIT true [get_sites SLICE_X30Y60]
set_property PROHIBIT true [get_sites SLICE_X31Y60]
set_property PROHIBIT true [get_sites SLICE_X32Y60]
set_property PROHIBIT true [get_sites SLICE_X33Y60]
set_property LOCK_PINS {I0:A1 I1:A2 I2:A3 I3:A4 I4:A6 I5:A5} [get_cells {tx/tx_data[2]_i_2}]
set_property LOCK_PINS {I0:A1 I1:A2 I2:A3 I3:A4 I4:A6 I5:A5} [get_cells {tx/tx_data[5]_i_2}]
set_property LOCK_PINS {I0:A1 I1:A2 I2:A3 I3:A4 I4:A6 I5:A5} [get_cells {tx/tx_data[6]_i_2}]
set_property LOCK_PINS {I0:A1 I1:A2 I2:A3 I3:A4 I4:A6 I5:A5} [get_cells {tx/tx_data[0]_i_2}]
set_property LOCK_PINS {I0:A1 I1:A2 I2:A3 I3:A4 I4:A6 I5:A5} [get_cells {tx/tx_data[1]_i_2}]
set_property LOCK_PINS {I0:A1 I1:A2 I2:A3 I3:A4 I4:A6 I5:A5} [get_cells {tx/tx_data[7]_i_3}]
set_property LOCK_PINS {I0:A1 I1:A2 I2:A3 I3:A4 I4:A6 I5:A5} [get_cells {tx/tx_data[3]_i_2}]
set_property LOCK_PINS {I0:A1 I1:A2 I2:A3 I3:A4 I4:A6 I5:A5} [get_cells {tx/tx_data[4]_i_2}]


