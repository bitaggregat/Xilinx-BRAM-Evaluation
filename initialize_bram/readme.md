# Create Partial Initialization Bitstream

This directory contains a script that creates a modified bitstream of a given FPGA for the experiment [see top level README for detail](../README.md)

## Bitstreams

3 different bitstreams are needed in order to start the experiment:

- A full bitstream containing UART + BRAM interface + BRAM initial values
- A partial bitstream that replaces the BRAM with a static return value
- A partial bitstream that re-replaces the static return value with bram again

These bitstreams can be generated using the already existing vivado project(s) ([See the vivado projects readme](../vivado_project/README.md))  

Pregenerated bitstreams can be found in ```/bitstreams```.

**Notes**:

- the second partial bitstream that replaces the partial design with bram again, will be modified by this script in order to initialize the bram **without values**

## Usage

Call the script with ```-h``` in order to get usage instructions.

```bash
python create_partial_initialization_bitstream.py -h
```