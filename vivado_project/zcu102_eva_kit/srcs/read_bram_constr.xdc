
#set_property IOSTANDARD LVCMOS18 [get_ports test_switch]
#set_property PACKAGE_PIN P2 [get_ports test_switch]

set_property PACKAGE_PIN B20 [get_ports uart_tx_o]
set_property IOSTANDARD LVCMOS33 [get_ports uart_tx_o]
set_property PACKAGE_PIN A22 [get_ports uart_rx_i]
set_property IOSTANDARD LVCMOS33 [get_ports uart_rx_i]
#set_property IOSTANDARD LVCMOS33 [get_ports sys_clk_p]
#set_property PACKAGE_PIN G21 [get_ports sys_clk_p]
#set_property IOSTANDARD LVCMOS18 [get_ports maxihpm0_lpd_aclk]
#set_property PACKAGE_PIN U15 [get_ports maxihpm0_lpd_aclk]

set_property IOSTANDARD LVCMOS33 [get_ports {led_o[7]}]
set_property IOSTANDARD LVCMOS33 [get_ports {led_o[6]}]
set_property IOSTANDARD LVCMOS33 [get_ports {led_o[5]}]
set_property IOSTANDARD LVCMOS33 [get_ports {led_o[4]}]
set_property IOSTANDARD LVCMOS33 [get_ports {led_o[3]}]
set_property IOSTANDARD LVCMOS33 [get_ports {led_o[2]}]
set_property IOSTANDARD LVCMOS33 [get_ports {led_o[1]}]
set_property IOSTANDARD LVCMOS33 [get_ports {led_o[0]}]

set_property PACKAGE_PIN AL12 [get_ports {led_o[7]}]
set_property PACKAGE_PIN AH14 [get_ports {led_o[6]}]
set_property PACKAGE_PIN AH13 [get_ports {led_o[5]}]
set_property PACKAGE_PIN AJ15 [get_ports {led_o[4]}]
set_property PACKAGE_PIN AJ14 [get_ports {led_o[3]}]
set_property PACKAGE_PIN AE13 [get_ports {led_o[2]}]
set_property PACKAGE_PIN AF13 [get_ports {led_o[1]}]
set_property PACKAGE_PIN AG14 [get_ports {led_o[0]}]





create_pblock pblock_2
resize_pblock [get_pblocks pblock_2] -add {SLICE_X82Y0:SLICE_X84Y59}
resize_pblock [get_pblocks pblock_2] -add {RAMB18_X11Y0:RAMB18_X11Y23}
resize_pblock [get_pblocks pblock_2] -add {RAMB36_X11Y0:RAMB36_X11Y11}
create_pblock pblock_3
resize_pblock [get_pblocks pblock_3] -add {SLICE_X79Y0:SLICE_X81Y59}
resize_pblock [get_pblocks pblock_3] -add {RAMB18_X10Y0:RAMB18_X10Y23}
resize_pblock [get_pblocks pblock_3] -add {RAMB36_X10Y0:RAMB36_X10Y11}
create_pblock pblock_4
resize_pblock [get_pblocks pblock_4] -add {SLICE_X70Y0:SLICE_X72Y59}
resize_pblock [get_pblocks pblock_4] -add {RAMB18_X9Y0:RAMB18_X9Y23}
resize_pblock [get_pblocks pblock_4] -add {RAMB36_X9Y0:RAMB36_X9Y11}
create_pblock pblock_5
resize_pblock [get_pblocks pblock_5] -add {SLICE_X64Y0:SLICE_X66Y59}
resize_pblock [get_pblocks pblock_5] -add {RAMB18_X8Y0:RAMB18_X8Y23}
resize_pblock [get_pblocks pblock_5] -add {RAMB36_X8Y0:RAMB36_X8Y11}
create_pblock pblock_6
resize_pblock [get_pblocks pblock_6] -add {SLICE_X58Y0:SLICE_X60Y59}
resize_pblock [get_pblocks pblock_6] -add {RAMB18_X7Y0:RAMB18_X7Y23}
resize_pblock [get_pblocks pblock_6] -add {RAMB36_X7Y0:RAMB36_X7Y11}
create_pblock pblock_7
resize_pblock [get_pblocks pblock_7] -add {SLICE_X46Y0:SLICE_X48Y59}
resize_pblock [get_pblocks pblock_7] -add {RAMB18_X6Y0:RAMB18_X6Y23}
resize_pblock [get_pblocks pblock_7] -add {RAMB36_X6Y0:RAMB36_X6Y11}
create_pblock pblock_8
resize_pblock [get_pblocks pblock_8] -add {SLICE_X37Y0:SLICE_X39Y59}
resize_pblock [get_pblocks pblock_8] -add {RAMB18_X5Y0:RAMB18_X5Y23}
resize_pblock [get_pblocks pblock_8] -add {RAMB36_X5Y0:RAMB36_X5Y11}
set_property SNAPPING_MODE ON [get_pblocks pblock_8]
create_pblock pblock_16
resize_pblock [get_pblocks pblock_16] -add {SLICE_X37Y60:SLICE_X39Y119}
resize_pblock [get_pblocks pblock_16] -add {RAMB18_X5Y24:RAMB18_X5Y47}
resize_pblock [get_pblocks pblock_16] -add {RAMB36_X5Y12:RAMB36_X5Y23}
create_pblock pblock_9
resize_pblock [get_pblocks pblock_9] -add {SLICE_X93Y60:SLICE_X95Y119}
resize_pblock [get_pblocks pblock_9] -add {RAMB18_X12Y24:RAMB18_X12Y47}
resize_pblock [get_pblocks pblock_9] -add {RAMB36_X12Y12:RAMB36_X12Y23}
create_pblock pblock_bram_wrap
set_property SNAPPING_MODE ON [get_pblocks pblock_bram_wrap]
create_pblock pblock_10
resize_pblock [get_pblocks pblock_10] -add {SLICE_X82Y60:SLICE_X84Y119}
resize_pblock [get_pblocks pblock_10] -add {RAMB18_X11Y24:RAMB18_X11Y47}
resize_pblock [get_pblocks pblock_10] -add {RAMB36_X11Y12:RAMB36_X11Y23}
set_property SNAPPING_MODE ON [get_pblocks pblock_10]
create_pblock pblock_11
resize_pblock [get_pblocks pblock_11] -add {SLICE_X79Y60:SLICE_X81Y119}
resize_pblock [get_pblocks pblock_11] -add {RAMB18_X10Y24:RAMB18_X10Y47}
resize_pblock [get_pblocks pblock_11] -add {RAMB36_X10Y12:RAMB36_X10Y23}
create_pblock pblock_12
resize_pblock [get_pblocks pblock_12] -add {SLICE_X70Y60:SLICE_X72Y119}
resize_pblock [get_pblocks pblock_12] -add {RAMB18_X9Y24:RAMB18_X9Y47}
resize_pblock [get_pblocks pblock_12] -add {RAMB36_X9Y12:RAMB36_X9Y23}
create_pblock pblock_13
resize_pblock [get_pblocks pblock_13] -add {SLICE_X64Y60:SLICE_X66Y119}
resize_pblock [get_pblocks pblock_13] -add {RAMB18_X8Y24:RAMB18_X8Y47}
resize_pblock [get_pblocks pblock_13] -add {RAMB36_X8Y12:RAMB36_X8Y23}
create_pblock pblock_14
resize_pblock [get_pblocks pblock_14] -add {SLICE_X58Y60:SLICE_X60Y119}
resize_pblock [get_pblocks pblock_14] -add {RAMB18_X7Y24:RAMB18_X7Y47}
resize_pblock [get_pblocks pblock_14] -add {RAMB36_X7Y12:RAMB36_X7Y23}
create_pblock pblock_15
resize_pblock [get_pblocks pblock_15] -add {SLICE_X46Y60:SLICE_X48Y119}
resize_pblock [get_pblocks pblock_15] -add {RAMB18_X6Y24:RAMB18_X6Y47}
resize_pblock [get_pblocks pblock_15] -add {RAMB36_X6Y12:RAMB36_X6Y23}
create_pblock pblock_17
resize_pblock [get_pblocks pblock_17] -add {SLICE_X93Y120:SLICE_X95Y179}
resize_pblock [get_pblocks pblock_17] -add {RAMB18_X12Y48:RAMB18_X12Y71}
resize_pblock [get_pblocks pblock_17] -add {RAMB36_X12Y24:RAMB36_X12Y35}
create_pblock pblock_18
resize_pblock [get_pblocks pblock_18] -add {SLICE_X82Y120:SLICE_X84Y179}
resize_pblock [get_pblocks pblock_18] -add {RAMB18_X11Y48:RAMB18_X11Y71}
resize_pblock [get_pblocks pblock_18] -add {RAMB36_X11Y24:RAMB36_X11Y35}
create_pblock pblock_19
resize_pblock [get_pblocks pblock_19] -add {SLICE_X79Y120:SLICE_X81Y179}
resize_pblock [get_pblocks pblock_19] -add {RAMB18_X10Y48:RAMB18_X10Y71}
resize_pblock [get_pblocks pblock_19] -add {RAMB36_X10Y24:RAMB36_X10Y35}
create_pblock pblock_20
resize_pblock [get_pblocks pblock_20] -add {SLICE_X70Y120:SLICE_X72Y179}
resize_pblock [get_pblocks pblock_20] -add {RAMB18_X9Y48:RAMB18_X9Y71}
resize_pblock [get_pblocks pblock_20] -add {RAMB36_X9Y24:RAMB36_X9Y35}
create_pblock pblock_21
resize_pblock [get_pblocks pblock_21] -add {SLICE_X64Y120:SLICE_X66Y179}
resize_pblock [get_pblocks pblock_21] -add {RAMB18_X8Y48:RAMB18_X8Y71}
resize_pblock [get_pblocks pblock_21] -add {RAMB36_X8Y24:RAMB36_X8Y35}
create_pblock pblock_22
resize_pblock [get_pblocks pblock_22] -add {SLICE_X58Y120:SLICE_X60Y179}
resize_pblock [get_pblocks pblock_22] -add {RAMB18_X7Y48:RAMB18_X7Y71}
resize_pblock [get_pblocks pblock_22] -add {RAMB36_X7Y24:RAMB36_X7Y35}
create_pblock pblock_23
resize_pblock [get_pblocks pblock_23] -add {SLICE_X46Y120:SLICE_X48Y179}
resize_pblock [get_pblocks pblock_23] -add {RAMB18_X6Y48:RAMB18_X6Y71}
resize_pblock [get_pblocks pblock_23] -add {RAMB36_X6Y24:RAMB36_X6Y35}
create_pblock pblock_24
resize_pblock [get_pblocks pblock_24] -add {SLICE_X37Y120:SLICE_X39Y179}
resize_pblock [get_pblocks pblock_24] -add {RAMB18_X5Y48:RAMB18_X5Y71}
resize_pblock [get_pblocks pblock_24] -add {RAMB36_X5Y24:RAMB36_X5Y35}
create_pblock pblock_25
resize_pblock [get_pblocks pblock_25] -add {SLICE_X93Y180:SLICE_X95Y239}
resize_pblock [get_pblocks pblock_25] -add {RAMB18_X12Y72:RAMB18_X12Y95}
resize_pblock [get_pblocks pblock_25] -add {RAMB36_X12Y36:RAMB36_X12Y47}
create_pblock pblock_26
resize_pblock [get_pblocks pblock_26] -add {SLICE_X82Y180:SLICE_X84Y239}
resize_pblock [get_pblocks pblock_26] -add {RAMB18_X11Y72:RAMB18_X11Y95}
resize_pblock [get_pblocks pblock_26] -add {RAMB36_X11Y36:RAMB36_X11Y47}
create_pblock pblock_27
resize_pblock [get_pblocks pblock_27] -add {SLICE_X79Y180:SLICE_X81Y239}
resize_pblock [get_pblocks pblock_27] -add {RAMB18_X10Y72:RAMB18_X10Y95}
resize_pblock [get_pblocks pblock_27] -add {RAMB36_X10Y36:RAMB36_X10Y47}
create_pblock pblock_28
resize_pblock [get_pblocks pblock_28] -add {SLICE_X70Y180:SLICE_X72Y239}
resize_pblock [get_pblocks pblock_28] -add {RAMB18_X9Y72:RAMB18_X9Y95}
resize_pblock [get_pblocks pblock_28] -add {RAMB36_X9Y36:RAMB36_X9Y47}
create_pblock pblock_29
resize_pblock [get_pblocks pblock_29] -add {SLICE_X64Y180:SLICE_X66Y239}
resize_pblock [get_pblocks pblock_29] -add {RAMB18_X8Y72:RAMB18_X8Y95}
resize_pblock [get_pblocks pblock_29] -add {RAMB36_X8Y36:RAMB36_X8Y47}
create_pblock pblock_30
resize_pblock [get_pblocks pblock_30] -add {SLICE_X58Y180:SLICE_X60Y239}
resize_pblock [get_pblocks pblock_30] -add {RAMB18_X7Y72:RAMB18_X7Y95}
resize_pblock [get_pblocks pblock_30] -add {RAMB36_X7Y36:RAMB36_X7Y47}
create_pblock pblock_31
resize_pblock [get_pblocks pblock_31] -add {SLICE_X46Y180:SLICE_X48Y239}
resize_pblock [get_pblocks pblock_31] -add {RAMB18_X6Y72:RAMB18_X6Y95}
resize_pblock [get_pblocks pblock_31] -add {RAMB36_X6Y36:RAMB36_X6Y47}
create_pblock pblock_32
resize_pblock [get_pblocks pblock_32] -add {SLICE_X37Y180:SLICE_X39Y239}
resize_pblock [get_pblocks pblock_32] -add {RAMB18_X5Y72:RAMB18_X5Y95}
resize_pblock [get_pblocks pblock_32] -add {RAMB36_X5Y36:RAMB36_X5Y47}
create_pblock pblock_33
resize_pblock [get_pblocks pblock_33] -add {SLICE_X93Y240:SLICE_X95Y299}
resize_pblock [get_pblocks pblock_33] -add {RAMB18_X12Y96:RAMB18_X12Y119}
resize_pblock [get_pblocks pblock_33] -add {RAMB36_X12Y48:RAMB36_X12Y59}
create_pblock pblock_34
resize_pblock [get_pblocks pblock_34] -add {SLICE_X82Y240:SLICE_X84Y299}
resize_pblock [get_pblocks pblock_34] -add {RAMB18_X11Y96:RAMB18_X11Y119}
resize_pblock [get_pblocks pblock_34] -add {RAMB36_X11Y48:RAMB36_X11Y59}
set_property SNAPPING_MODE ON [get_pblocks pblock_34]
create_pblock pblock_35
resize_pblock [get_pblocks pblock_35] -add {SLICE_X79Y240:SLICE_X81Y299}
resize_pblock [get_pblocks pblock_35] -add {RAMB18_X10Y96:RAMB18_X10Y119}
resize_pblock [get_pblocks pblock_35] -add {RAMB36_X10Y48:RAMB36_X10Y59}
create_pblock pblock_36
resize_pblock [get_pblocks pblock_36] -add {SLICE_X70Y240:SLICE_X72Y299}
resize_pblock [get_pblocks pblock_36] -add {RAMB18_X9Y96:RAMB18_X9Y119}
resize_pblock [get_pblocks pblock_36] -add {RAMB36_X9Y48:RAMB36_X9Y59}
create_pblock pblock_37
resize_pblock [get_pblocks pblock_37] -add {SLICE_X64Y240:SLICE_X66Y299}
resize_pblock [get_pblocks pblock_37] -add {RAMB18_X8Y96:RAMB18_X8Y119}
resize_pblock [get_pblocks pblock_37] -add {RAMB36_X8Y48:RAMB36_X8Y59}
create_pblock pblock_38
resize_pblock [get_pblocks pblock_38] -add {SLICE_X58Y240:SLICE_X60Y299}
resize_pblock [get_pblocks pblock_38] -add {RAMB18_X7Y96:RAMB18_X7Y119}
resize_pblock [get_pblocks pblock_38] -add {RAMB36_X7Y48:RAMB36_X7Y59}
create_pblock pblock_39
resize_pblock [get_pblocks pblock_39] -add {SLICE_X46Y240:SLICE_X48Y299}
resize_pblock [get_pblocks pblock_39] -add {RAMB18_X6Y96:RAMB18_X6Y119}
resize_pblock [get_pblocks pblock_39] -add {RAMB36_X6Y48:RAMB36_X6Y59}
create_pblock pblock_40
resize_pblock [get_pblocks pblock_40] -add {SLICE_X37Y240:SLICE_X39Y299}
resize_pblock [get_pblocks pblock_40] -add {RAMB18_X5Y96:RAMB18_X5Y119}
resize_pblock [get_pblocks pblock_40] -add {RAMB36_X5Y48:RAMB36_X5Y59}
create_pblock pblock_41
resize_pblock [get_pblocks pblock_41] -add {SLICE_X93Y300:SLICE_X95Y359}
resize_pblock [get_pblocks pblock_41] -add {RAMB18_X12Y120:RAMB18_X12Y143}
resize_pblock [get_pblocks pblock_41] -add {RAMB36_X12Y60:RAMB36_X12Y71}
create_pblock pblock_42
resize_pblock [get_pblocks pblock_42] -add {SLICE_X82Y300:SLICE_X84Y359}
resize_pblock [get_pblocks pblock_42] -add {RAMB18_X11Y120:RAMB18_X11Y143}
resize_pblock [get_pblocks pblock_42] -add {RAMB36_X11Y60:RAMB36_X11Y71}
create_pblock pblock_43
resize_pblock [get_pblocks pblock_43] -add {SLICE_X79Y300:SLICE_X81Y359}
resize_pblock [get_pblocks pblock_43] -add {RAMB18_X10Y120:RAMB18_X10Y143}
resize_pblock [get_pblocks pblock_43] -add {RAMB36_X10Y60:RAMB36_X10Y71}
create_pblock pblock_44
resize_pblock [get_pblocks pblock_44] -add {SLICE_X70Y300:SLICE_X72Y359}
resize_pblock [get_pblocks pblock_44] -add {RAMB18_X9Y120:RAMB18_X9Y143}
resize_pblock [get_pblocks pblock_44] -add {RAMB36_X9Y60:RAMB36_X9Y71}
create_pblock pblock_45
resize_pblock [get_pblocks pblock_45] -add {SLICE_X64Y300:SLICE_X66Y359}
resize_pblock [get_pblocks pblock_45] -add {RAMB18_X8Y120:RAMB18_X8Y143}
resize_pblock [get_pblocks pblock_45] -add {RAMB36_X8Y60:RAMB36_X8Y71}
create_pblock pblock_46
resize_pblock [get_pblocks pblock_46] -add {SLICE_X58Y300:SLICE_X60Y359}
resize_pblock [get_pblocks pblock_46] -add {RAMB18_X7Y120:RAMB18_X7Y143}
resize_pblock [get_pblocks pblock_46] -add {RAMB36_X7Y60:RAMB36_X7Y71}
create_pblock pblock_49
resize_pblock [get_pblocks pblock_49] -add {SLICE_X91Y360:SLICE_X95Y419}
resize_pblock [get_pblocks pblock_49] -add {RAMB18_X12Y144:RAMB18_X12Y167}
resize_pblock [get_pblocks pblock_49] -add {RAMB36_X12Y72:RAMB36_X12Y83}
create_pblock pblock_50
resize_pblock [get_pblocks pblock_50] -add {SLICE_X82Y360:SLICE_X85Y419}
resize_pblock [get_pblocks pblock_50] -add {RAMB18_X11Y144:RAMB18_X11Y167}
resize_pblock [get_pblocks pblock_50] -add {RAMB36_X11Y72:RAMB36_X11Y83}
create_pblock pblock_51
resize_pblock [get_pblocks pblock_51] -add {SLICE_X77Y360:SLICE_X81Y419}
resize_pblock [get_pblocks pblock_51] -add {RAMB18_X10Y144:RAMB18_X10Y167}
resize_pblock [get_pblocks pblock_51] -add {RAMB36_X10Y72:RAMB36_X10Y83}
create_pblock pblock_52
resize_pblock [get_pblocks pblock_52] -add {SLICE_X68Y360:SLICE_X73Y419}
resize_pblock [get_pblocks pblock_52] -add {RAMB18_X9Y144:RAMB18_X9Y167}
resize_pblock [get_pblocks pblock_52] -add {RAMB36_X9Y72:RAMB36_X9Y83}
create_pblock pblock_53
resize_pblock [get_pblocks pblock_53] -add {SLICE_X62Y360:SLICE_X67Y419}
resize_pblock [get_pblocks pblock_53] -add {RAMB18_X8Y144:RAMB18_X8Y167}
resize_pblock [get_pblocks pblock_53] -add {RAMB36_X8Y72:RAMB36_X8Y83}
create_pblock pblock_54
resize_pblock [get_pblocks pblock_54] -add {SLICE_X56Y360:SLICE_X61Y419}
resize_pblock [get_pblocks pblock_54] -add {RAMB18_X7Y144:RAMB18_X7Y167}
resize_pblock [get_pblocks pblock_54] -add {RAMB36_X7Y72:RAMB36_X7Y83}
create_pblock pblock_47
resize_pblock [get_pblocks pblock_47] -add {SLICE_X46Y300:SLICE_X48Y359}
resize_pblock [get_pblocks pblock_47] -add {RAMB18_X6Y120:RAMB18_X6Y143}
resize_pblock [get_pblocks pblock_47] -add {RAMB36_X6Y60:RAMB36_X6Y71}
create_pblock pblock_48
resize_pblock [get_pblocks pblock_48] -add {SLICE_X37Y300:SLICE_X39Y359}
resize_pblock [get_pblocks pblock_48] -add {RAMB18_X5Y120:RAMB18_X5Y143}
resize_pblock [get_pblocks pblock_48] -add {RAMB36_X5Y60:RAMB36_X5Y71}
create_pblock pblock_55
resize_pblock [get_pblocks pblock_55] -add {SLICE_X44Y360:SLICE_X49Y419}
resize_pblock [get_pblocks pblock_55] -add {RAMB18_X6Y144:RAMB18_X6Y167}
resize_pblock [get_pblocks pblock_55] -add {RAMB36_X6Y72:RAMB36_X6Y83}
create_pblock pblock_56
resize_pblock [get_pblocks pblock_56] -add {SLICE_X35Y360:SLICE_X40Y419}
resize_pblock [get_pblocks pblock_56] -add {RAMB18_X5Y144:RAMB18_X5Y167}
resize_pblock [get_pblocks pblock_56] -add {RAMB36_X5Y72:RAMB36_X5Y83}
create_pblock pblock_57
resize_pblock [get_pblocks pblock_57] -add {SLICE_X31Y180:SLICE_X33Y239}
resize_pblock [get_pblocks pblock_57] -add {RAMB18_X4Y72:RAMB18_X4Y95}
resize_pblock [get_pblocks pblock_57] -add {RAMB36_X4Y36:RAMB36_X4Y47}
set_property SNAPPING_MODE ON [get_pblocks pblock_57]
create_pblock pblock_58
resize_pblock [get_pblocks pblock_58] -add {SLICE_X22Y180:SLICE_X24Y239}
resize_pblock [get_pblocks pblock_58] -add {RAMB18_X3Y72:RAMB18_X3Y95}
resize_pblock [get_pblocks pblock_58] -add {RAMB36_X3Y36:RAMB36_X3Y47}
set_property SNAPPING_MODE ON [get_pblocks pblock_58]
create_pblock pblock_59
resize_pblock [get_pblocks pblock_59] -add {SLICE_X16Y180:SLICE_X18Y239}
resize_pblock [get_pblocks pblock_59] -add {RAMB18_X2Y72:RAMB18_X2Y95}
resize_pblock [get_pblocks pblock_59] -add {RAMB36_X2Y36:RAMB36_X2Y47}
set_property SNAPPING_MODE ON [get_pblocks pblock_59]
create_pblock pblock_60
resize_pblock [get_pblocks pblock_60] -add {SLICE_X7Y180:SLICE_X9Y239}
resize_pblock [get_pblocks pblock_60] -add {RAMB18_X1Y72:RAMB18_X1Y95}
resize_pblock [get_pblocks pblock_60] -add {RAMB36_X1Y36:RAMB36_X1Y47}
set_property SNAPPING_MODE ON [get_pblocks pblock_60]
create_pblock pblock_61
resize_pblock [get_pblocks pblock_61] -add {SLICE_X0Y180:SLICE_X4Y239}
resize_pblock [get_pblocks pblock_61] -add {RAMB18_X0Y72:RAMB18_X0Y95}
resize_pblock [get_pblocks pblock_61] -add {RAMB36_X0Y36:RAMB36_X0Y47}
create_pblock pblock_62
resize_pblock [get_pblocks pblock_62] -add {SLICE_X31Y240:SLICE_X33Y299}
resize_pblock [get_pblocks pblock_62] -add {RAMB18_X4Y96:RAMB18_X4Y119}
resize_pblock [get_pblocks pblock_62] -add {RAMB36_X4Y48:RAMB36_X4Y59}
create_pblock pblock_63
resize_pblock [get_pblocks pblock_63] -add {SLICE_X22Y240:SLICE_X24Y299}
resize_pblock [get_pblocks pblock_63] -add {RAMB18_X3Y96:RAMB18_X3Y119}
resize_pblock [get_pblocks pblock_63] -add {RAMB36_X3Y48:RAMB36_X3Y59}
create_pblock pblock_64
resize_pblock [get_pblocks pblock_64] -add {SLICE_X16Y240:SLICE_X18Y299}
resize_pblock [get_pblocks pblock_64] -add {RAMB18_X2Y96:RAMB18_X2Y119}
resize_pblock [get_pblocks pblock_64] -add {RAMB36_X2Y48:RAMB36_X2Y59}
create_pblock pblock_65
resize_pblock [get_pblocks pblock_65] -add {SLICE_X7Y240:SLICE_X9Y299}
resize_pblock [get_pblocks pblock_65] -add {RAMB18_X1Y96:RAMB18_X1Y119}
resize_pblock [get_pblocks pblock_65] -add {RAMB36_X1Y48:RAMB36_X1Y59}
create_pblock pblock_66
resize_pblock [get_pblocks pblock_66] -add {SLICE_X0Y240:SLICE_X4Y299}
resize_pblock [get_pblocks pblock_66] -add {RAMB18_X0Y96:RAMB18_X0Y119}
resize_pblock [get_pblocks pblock_66] -add {RAMB36_X0Y48:RAMB36_X0Y59}
create_pblock pblock_67
resize_pblock [get_pblocks pblock_67] -add {SLICE_X31Y300:SLICE_X33Y359}
resize_pblock [get_pblocks pblock_67] -add {RAMB18_X4Y120:RAMB18_X4Y143}
resize_pblock [get_pblocks pblock_67] -add {RAMB36_X4Y60:RAMB36_X4Y71}
create_pblock pblock_68
resize_pblock [get_pblocks pblock_68] -add {SLICE_X22Y300:SLICE_X24Y359}
resize_pblock [get_pblocks pblock_68] -add {RAMB18_X3Y120:RAMB18_X3Y143}
resize_pblock [get_pblocks pblock_68] -add {RAMB36_X3Y60:RAMB36_X3Y71}
create_pblock pblock_69
resize_pblock [get_pblocks pblock_69] -add {SLICE_X16Y300:SLICE_X18Y359}
resize_pblock [get_pblocks pblock_69] -add {RAMB18_X2Y120:RAMB18_X2Y143}
resize_pblock [get_pblocks pblock_69] -add {RAMB36_X2Y60:RAMB36_X2Y71}
create_pblock pblock_70
resize_pblock [get_pblocks pblock_70] -add {SLICE_X7Y300:SLICE_X9Y359}
resize_pblock [get_pblocks pblock_70] -add {RAMB18_X1Y120:RAMB18_X1Y143}
resize_pblock [get_pblocks pblock_70] -add {RAMB36_X1Y60:RAMB36_X1Y71}
create_pblock pblock_71
add_cells_to_pblock [get_pblocks pblock_71] [get_cells -quiet [list bram_wrap]]
resize_pblock [get_pblocks pblock_71] -add {SLICE_X0Y300:SLICE_X4Y359}
resize_pblock [get_pblocks pblock_71] -add {RAMB18_X0Y120:RAMB18_X0Y143}
resize_pblock [get_pblocks pblock_71] -add {RAMB36_X0Y60:RAMB36_X0Y71}
set_property SNAPPING_MODE ON [get_pblocks pblock_71]
create_pblock pblock_72
resize_pblock [get_pblocks pblock_72] -add {SLICE_X29Y360:SLICE_X34Y419}
resize_pblock [get_pblocks pblock_72] -add {RAMB18_X4Y144:RAMB18_X4Y167}
resize_pblock [get_pblocks pblock_72] -add {RAMB36_X4Y72:RAMB36_X4Y83}
create_pblock pblock_73
resize_pblock [get_pblocks pblock_73] -add {SLICE_X20Y360:SLICE_X25Y419}
resize_pblock [get_pblocks pblock_73] -add {RAMB18_X3Y144:RAMB18_X3Y167}
resize_pblock [get_pblocks pblock_73] -add {RAMB36_X3Y72:RAMB36_X3Y83}
create_pblock pblock_74
resize_pblock [get_pblocks pblock_74] -add {SLICE_X14Y360:SLICE_X19Y419}
resize_pblock [get_pblocks pblock_74] -add {RAMB18_X2Y144:RAMB18_X2Y167}
resize_pblock [get_pblocks pblock_74] -add {RAMB36_X2Y72:RAMB36_X2Y83}
create_pblock pblock_75
resize_pblock [get_pblocks pblock_75] -add {SLICE_X5Y360:SLICE_X10Y419}
resize_pblock [get_pblocks pblock_75] -add {RAMB18_X1Y144:RAMB18_X1Y167}
resize_pblock [get_pblocks pblock_75] -add {RAMB36_X1Y72:RAMB36_X1Y83}
create_pblock pblock_76
resize_pblock [get_pblocks pblock_76] -add {SLICE_X0Y360:SLICE_X4Y419}
resize_pblock [get_pblocks pblock_76] -add {RAMB18_X0Y144:RAMB18_X0Y167}
resize_pblock [get_pblocks pblock_76] -add {RAMB36_X0Y72:RAMB36_X0Y83}
set_property SNAPPING_MODE ON [get_pblocks pblock_76]


set_property PROHIBIT true [get_sites SLICE_X1Y360]
set_property PROHIBIT true [get_sites SLICE_X2Y360]
set_property PROHIBIT true [get_sites SLICE_X3Y360]

set_property PROHIBIT true [get_sites SLICE_X82Y240]
set_property PROHIBIT true [get_sites SLICE_X83Y240]
set_property PROHIBIT true [get_sites SLICE_X84Y240]









set_property PROHIBIT true [get_sites RAMB36_X4Y36]

set_property PROHIBIT true [get_sites RAMB36_X4Y37]

set_property PROHIBIT true [get_sites RAMB36_X4Y38]

set_property PROHIBIT true [get_sites RAMB36_X4Y39]

set_property PROHIBIT true [get_sites RAMB36_X4Y40]

set_property PROHIBIT true [get_sites RAMB36_X4Y41]

set_property PROHIBIT true [get_sites RAMB36_X4Y42]

set_property PROHIBIT true [get_sites RAMB36_X4Y43]

set_property PROHIBIT true [get_sites RAMB36_X4Y44]

set_property PROHIBIT true [get_sites RAMB36_X4Y45]

set_property PROHIBIT true [get_sites RAMB36_X4Y46]


set_property PROHIBIT true [get_sites RAMB36_X3Y36]

set_property PROHIBIT true [get_sites RAMB36_X3Y37]

set_property PROHIBIT true [get_sites RAMB36_X3Y38]

set_property PROHIBIT true [get_sites RAMB36_X3Y39]

set_property PROHIBIT true [get_sites RAMB36_X3Y40]

set_property PROHIBIT true [get_sites RAMB36_X3Y41]

set_property PROHIBIT true [get_sites RAMB36_X3Y42]

set_property PROHIBIT true [get_sites RAMB36_X3Y43]

set_property PROHIBIT true [get_sites RAMB36_X3Y44]

set_property PROHIBIT true [get_sites RAMB36_X3Y45]

set_property PROHIBIT true [get_sites RAMB36_X3Y46]


set_property PROHIBIT true [get_sites RAMB36_X2Y36]

set_property PROHIBIT true [get_sites RAMB36_X2Y37]

set_property PROHIBIT true [get_sites RAMB36_X2Y38]

set_property PROHIBIT true [get_sites RAMB36_X2Y39]

set_property PROHIBIT true [get_sites RAMB36_X2Y40]

set_property PROHIBIT true [get_sites RAMB36_X2Y41]

set_property PROHIBIT true [get_sites RAMB36_X2Y42]

set_property PROHIBIT true [get_sites RAMB36_X2Y43]

set_property PROHIBIT true [get_sites RAMB36_X2Y44]

set_property PROHIBIT true [get_sites RAMB36_X2Y45]

set_property PROHIBIT true [get_sites RAMB36_X2Y46]


set_property PROHIBIT true [get_sites RAMB36_X1Y36]

set_property PROHIBIT true [get_sites RAMB36_X1Y37]

set_property PROHIBIT true [get_sites RAMB36_X1Y38]

set_property PROHIBIT true [get_sites RAMB36_X1Y39]

set_property PROHIBIT true [get_sites RAMB36_X1Y40]

set_property PROHIBIT true [get_sites RAMB36_X1Y41]

set_property PROHIBIT true [get_sites RAMB36_X1Y42]

set_property PROHIBIT true [get_sites RAMB36_X1Y43]

set_property PROHIBIT true [get_sites RAMB36_X1Y44]

set_property PROHIBIT true [get_sites RAMB36_X1Y45]

set_property PROHIBIT true [get_sites RAMB36_X1Y46]

set_property PROHIBIT true [get_sites SLICE_X7Y239]
set_property PROHIBIT true [get_sites SLICE_X8Y239]
set_property PROHIBIT true [get_sites SLICE_X9Y239]
create_pblock pblock_1
resize_pblock [get_pblocks pblock_1] -add {SLICE_X92Y0:SLICE_X95Y59}
resize_pblock [get_pblocks pblock_1] -add {RAMB18_X12Y0:RAMB18_X12Y23}
resize_pblock [get_pblocks pblock_1] -add {RAMB36_X12Y0:RAMB36_X12Y11}


