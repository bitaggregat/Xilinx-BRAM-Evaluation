# Full Bitstream Initialization

According to [UG573](https://gitlab.bitaggregat.de/hwt/wissensspeicher/-/blob/main/Manuals/Xilinx/UltraScale/ug573-ultrascale-memory-resources.pdf?ref_type=heads), BRAM will be assigned the value 0 if a no value is specified.  
This assignment happens somewhere upon device startup.  
A workaround for this is the usage of partial bitstreams, because partial bitstreams don't cause a full startup.

The existence of the "default zero assignment" was verified for XCUS+ devices.  
The details are found below.

## XCUS+ (te0802)

### Bitstream manipulation

- full bitstream that fills bram with ff was used (read_BRAM_X16Y65_RAMB36_X2Y14_ff_full.bit)
- byteman was used to turn the binary bitstream (.bit) into bitasm (human readable Bitstream Frame Format) with following command:

```bash
./Binaries/Linux-x86/byteman Xilinx UltraScale+ -assembly read_BRAM_X16Y65_RAMB36_X2Y14_ff_full.bit temp.bitasm
```

- all Frames with ```BlockType=1``` (BRAM writes) were manually removed from temp.bitasm
- ```@FDRI for #n frames:``` was adapted such that n fitted the frame count
- checksum (crc) checks were removed from bitasm
- bitasm was turned into .bit again:

```bash
./Binaries/Linux-x86/byteman Xilinx UltraScale+ -assembly temp.bitasm read_BRAM_X16Y65_RAMB36_X2Y14_ff_full_without_bram_frames.bit
```

- bitstream was flashed
- readout was done (UART interface is already included in bitstream)

### Results

- Only zeros were read (as expected)
- partial bitstreams are needed to access the actual startup bram value
