# Reading BRAM via ftdi

This directory contains a simple python script that readouts bram from an fpga using JTAG via an ftdi chip and UART.  
It also uses a "custom protocol" that is in accordance with [TODO insert link]().  

## Usage

Call the script with ```-h``` in order to get the latest usage instructions

```bash
python read_bram_ftdi.py -h
```

## Dependencies

- [pyftdi](https://eblot.github.io/pyftdi/)

