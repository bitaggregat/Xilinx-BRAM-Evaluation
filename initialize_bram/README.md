# initialize_bram

This directory contains a script that initializes the bram blocks of a given FPGA for the experiment [see top level README for detail](../README.md)

## Usage

```--help``` output of the script:

```bash
usage: initialize_bram.py [-h] -nb BRAMLESS_BS -fb BRAM_FULL_BS -pb BRAM_PARTIAL_BS [-a FIRST_BRAM_FRAME_ADDRESS]
                          [-t WAIT_TIME]

Script that takes an three input bitstreams, then initializes FPGA for BRAM experiment, measure.

options:
  -h, --help            show this help message and exit
  -nb BRAMLESS_BS, --bramless_bs BRAMLESS_BS
                        Path to partial bramless Bitstream file that initializes Target Region with a design that
                        does not use BRAM blocks. This cuts the power to the previously initiated BRAM Block(s)
  -fb BRAM_FULL_BS, --bram_full_bs BRAM_FULL_BS
                        Path to Bitstream file that initializes Target Region with a design that uses BRAM blocks,
                        initializes their values and initializes a communication interface/protocol IP in another
                        region of the FPGA. This cuts the power to the previously initiated BRAM Block(s)
  -pb BRAM_PARTIAL_BS, --bram_partial_bs BRAM_PARTIAL_BS
                        Partial version of "bram_full_bs" (path to partial bitstream).NOTE: BOTH "--bram_full_bs" AND
                        "--bram_partial_bs" are required.
  -a FIRST_BRAM_FRAME_ADDRESS, --first_bram_frame_address FIRST_BRAM_FRAME_ADDRESS
                        Address of the first frame with bram content as hex string. This can vary depending on the
                        region the partial design is located in. -Can be looked up by unpacking '--bram_partial_bs'.
                        -Will be >= 00c00000 (usually 00c00080 or 00c00000)
  -t WAIT_TIME, --wait_time WAIT_TIME
                        Time that will be waited for while bram is depowered in seconds. Note: Having the bram
                        depowered for longer may enhance results.
```

## Bitstreams

3 different bitstreams are needed in order to start the experiment:

- A full bitstream containing UART + BRAM interface + BRAM initial values
- A partial bitstream that replaces the BRAM with a static return value
- A partial bitstream that re-replaces the static return value with bram again

These bitstreams can be generated using the already existing vivado project(s) ([See the vivado projects readme](../vivado_project/README.md))  

Pregenerated bitstreams can be found in ```/bitstreams```.

**Notes**:

- the second partial bitstream that replaces the partial design with bram again, will be modified by this script in order to initialize the bram **without values**

### Pregenerated bitstream names

The table below explains the content of the pregenerated bitstreams.

#### pblock3

|Bitstream name|Usage|Explanation|
|-|-|-|
|```bramless_return_0_partial.bit``` | nb | Bramless partial bitstream,<br> implements static design that returns 0's from LUTS|
|```bramless_return_f_partial.bit``` | nb | Bramless partial bitstream,<br> implements static design that returns 1's from LUTS|
|```read_BRAM_X30Y35_RAMB_X1Y6_00_full.bit``` | fb | Full bitstream, <br> implements UART interface, connects UART to bram,<br> initializes bram with 0's,<br> uses RAM block at position X1Y6 on FPGA grid|
|```read_BRAM_X30Y35_RAMB_X1Y6_ff_full.bit``` | fb | Same as ```read_BRAM_X30Y35_RAMB_X1Y6_00_full.bit```,<br> but initializes with 1's|
|```read_BRAM_X30Y35_RAMB_X1Y7_00_full.bit``` | fb | Same as ```read_BRAM_X30Y35_RAMB_X1Y6_00_full.bit```,<br> but uses RAM block X1Y7|
|```read_BRAM_X30Y35_RAMB_X1Y7_ff_full.bit``` | fb | Same as ```read_BRAM_X30Y35_RAMB_X1Y6_ff_full.bit```,<br> but uses RAM block X1Y7|
|```read_BRAM_X30Y35_RAMB_X1Y8_00_full.bit``` | fb | Same as ```read_BRAM_X30Y35_RAMB_X1Y6_00_full.bit```,<br> but uses RAM block X1Y8|
|```read_BRAM_X30Y35_RAMB_X1Y8_ff_full.bit``` | fb | Same as ```read_BRAM_X30Y35_RAMB_X1Y6_ff_full.bit```,<br> but uses RAM block X1Y8|
| ```read_BRAM_X30Y35_RAMB_X1Y6_ff_partial.bit``` | pb | Partial bitstream,<br> reactivates bram and initializes it with 1's,<br> uses RAM block X1X6|
| ```read_BRAM_X30Y35_RAMB_X1Y7_ff_partial.bit``` | pb | Same as ```read_BRAM_X30Y35_RAMB_X1Y6_ff_partial.bit```<br> but uses RAM block X1X7|
| ```read_BRAM_X30Y35_RAMB_X1Y6_ff_partial.bit``` | pb | Same as ```read_BRAM_X30Y35_RAMB_X1Y8_ff_partial.bit```<br> but uses RAM block X1X8|