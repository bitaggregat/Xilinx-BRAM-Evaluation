# Configware

This directory contains the HDL sources and scripts that create the bram readout FPGA Design.

## Rebuild the Vivado project

- Open a tcl console in Vivado
- cd to the directory where ```read_bram_partial.tcl``` is located
- ```source read_bram_partial.tcl```
- Sometimes you will additionally need to:
  - open "Dynamic Function eXchange Wizard" (on the left side)
  - click next until you are in the "Edit Configuration Runs" window
  - click on "Standard DFX" (in the center) and use the default options

## Sources based from other projects

The following files are modified versions of files from a [third party repository](https://github.com/FlippingLogic/fpga_read_bram):

- srcs/new_uart.v
- srcs/read_bram.v
