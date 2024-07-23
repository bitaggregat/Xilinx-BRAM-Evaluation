# Documentation on XC7 FPGA SRAM PUFs

## General

SRAMs can have an initial value different from 0 when being switched on.  
These initial values can potentially used to implement a PUF.  
This Readme sums up what has been done/found out/tested about possible SRAM PUFs on XC7 FPGAs.  
The procedure used for our tests includes manipulation of bitstreams (bs) and is documented here aswell.

## Current Status

Following the instructions of the [Paper by Wild & Güneysu 2014](https://gitlab.bitaggregat.de/hwt/hardware-security-module/hsm.pages.bitaggregat.de/uploads/d757e7e215824307a9c7764a4860b0d7/wild2014.pdf) led to some flipped bits in the SRAM (BRAM Blocks). The results are documented below.

## Measured Stats

### Basys3 (xc7a35tcpg236-1)

These measurements were done on our local basys3 board. (sticker on the downside of the board: **DA89AC3**).  
Measurements were done on:

- 3 x 36K BRAM Blocks
- All 3 BRAM Blocks were within the same row of the FPGA
- Parity and Data bits were used
- Each BRAM Block was measured 4 times (named Read 1, Read 2 ...)
- "-" stands for "no bitlfip"

|Tile and Slice|BRAM value before power outage|% of flipped bits in data|% of flipped bits in parity|other|
|--------------|------------------------------|---------------------------|---------------------------|-----|
|BRAM_X30Y35_RAMB_X1Y6|ff|0|0|-|
|BRAM_X30Y35_RAMB_X1Y6|00|0.00024606299212598425|0|-|
|BRAM_X30Y35_RAMB_X1Y7|ff|0|0|-|
|BRAM_X30Y35_RAMB_X1Y7|00|0.0002768208661417323|0|-|
|BRAM_X30Y35_RAMB_X1Y7|ff|0|0|-|
|BRAM_X30Y35_RAMB_X1Y7|00|0.00024606299212598425|0|-|
|BRAM_X30Y35_RAMB_X1Y6|00|~0.005580357142857143|0|initializing BRAM without values 100 times consecutively|

#### BRAM_X30Y35_RAMB_X1Y6

|Position|Read 1|Read 2|Read 3|Read 4|
|-|-|-|-|-|
|3607|c0|c0|c0|c0|
|3615|-|-|-|40|
|3647|40|40|40|40|
|3671|-|-|-|80|
|3690|80|80|80|80|
|3691|80|-|80|80|
|4055|80|80|80|80|
|4063|-|-|-|80|
|4095|c0|c0|c0|c0|

#### BRAM_X30Y35_RAMB_X1Y7

|Position|Read 1 |All other Reads|
|-|-|-|
|131|40|40|
|419|c0|c0|
|1523|40|40|
|3007|80|80|
|3438|**82**|80|
|4095|c0|c0|

#### BRAM_X30Y35_RAMB_X1Y8

|Position|Read 1|Read 2|Read 3|Read 4|
|-|-|-|-|-|
|1370|02|02|02|02|
|1371|**82**|**80**|**02**|**82**|
|1635|40|40|40|40|
|1891|c0|c0|c0|c0|
|1899|-|40|-|-|
|1911|80|80|80|80|
|3959|-|80|-|-|
|4075|40|40|40|40|
|4091|-|40|-|-|

### Problem

- The amount of flipped bits is low normally on the basys3
- Flashing the partial bitstream that reactivates the bram (without initializing it's values) increases the amount of flipped bits by a great amount

#### <a name="link1"></a> Initializing BRAM without values multiple times

- The amount of flipped bits increased alot by doing this
- We looked at the flipped bits from a **byte level** perspective
- But the flipped **bytes** were predictable
- e.g. flashing 100 times led to many ```c0```, ```80``` and ```40```'s
- flasing 1000 times led to more variety in flipped bytes (e.g ```01```, ```41```, ```82```)
- There seems to be a correlation between amount of times the bram was activated and randomness of the bram content
- Tests using a heat gun showed that this phenomenon is **NOT** temperature related

## Notes on Process

### XC7 BRAMs

- One BRAM Tile can store 36608 bits (4096 Data Bytes + 480 Parity Bytes)
- Parity Bytes can also be used as additional data bytes
- Helper Scripts exist:

|Name|Use case|
|-|-|
|```initialize_bram.py```|Takes previously prepared bram bitstreams, modifies and flashes the latter such that bram is depowered, then repowered for reading|
|```read_bram_ftdi.py```|Reads out bram via ftdi uart. Uses a custom protocol to identify beginning of readout and parity bram bits (which are just glorified additional bram bits)|

**NOTES**:

- ```initialize_bram.py``` uses a "custom bitstream editor" (see bitstream_handling/README.md).
- using the custom editor with a python debugger is ideal for inspecting details about the bitstream
- TODO helper script ```analyze_bitstream.py``` to automatize use cases of the editor code base

### How To

#### General Approach

![Visualization of Readout Design](bram_partial.drawio.png)

1. Create a partial design in Vivado (fill BRAM with either 0 or f)
2. Flash "Read BRAM Design" config as full bitstream
3. Flash "Non BRAM Design" config as partial bitstream (this will disconnect BRAM from power)
4. Modify "Read BRAM Design" partial bitstream such that BRAM will be initiated but without values
5. Flash modified partial bitstream
6. Readout BRAM via UART

#### Practical Approach

- Step 1 is contained in [a vivado project](/vivado_project/README.md) of this repository
- Step 2 - 5 can be done by calling ```initialize_bram.py```
- Step 6 can be done via ```read_bram_ftdi.py```

Note: All these scripts named above can be called with ```-h``` for usage information.

#### Additions

- A wait time can be inserted between Step 3 and 5
- Repeating Step 5 multiple times yields interesting results [see previous section](#link1)
