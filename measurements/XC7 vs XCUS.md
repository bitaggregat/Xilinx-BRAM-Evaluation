# 7-Series vs UltraScale(+) Bitstream differences

7-Series and UltraScale(+) FPGAs are two product lines/architectures of Xilinx FPGAs.  
This document describes how much their bitstream format differs.  
- [XCUS Configuration Doc](https://gitlab.bitaggregat.de/hwt/wissensspeicher/-/blob/main/Manuals/Xilinx/UltraScale/ug570-ultrascale-configuration.pdf?ref_type=heads)(Which includes UltraScale+)
- [XC7 Configuration Doc](https://gitlab.bitaggregat.de/hwt/wissensspeicher/-/blob/main/Manuals/Xilinx/7-Series/ug470_7Series_Config.pdf?ref_type=heads)

## Configuration Packets

The Format of Configuration Packets remains unchanged between the two Architectures.  
With one exception:

- ZynqMP bitstreams seem to divide the packages into "badges"
- The configuration bus is, disconnected (via FFFFFFFF spacing signal) and reconnected again (via Synch Word), between badges
- This could also be feature unique to Zynq devices (Future TODO: verify this)

## Configuration Registers

The configuration registers were almost the same.
Exceptions:

- the "RBCRC_SW" register is mentioned in XC7 documentation but not in XCUS documentation
- although "RBCRC_SW" may still exist on XCUS fpgas and was just dissimulated from the documentation

### Address

Each Configuration Register has an Address.  

- Addresses of Registers is same between the two Architectures.  
- Exception: RBCRC_SW with addr ```10011```, is not listed in UltraScale Doc

### Register Content

- Content of registers differs slightly between the two Architectures
- FDRI, FDRO and FAR did not change
- CTL and COR registers differ
- differences are probably due to changes in bitstream encryption between the two Architectures

## Configuration Data (Frame Data)

- Differences can be indirectly be read seen by comparing [prjxray](https://github.com/f4pga/prjxray-db)s and [prjuray](https://github.com/f4pga/prjuray-db)s FASM databases
- The details are currently not relevant and may be future work

## Conclusion

Tools/Code that handles 7-Series bitstream can also be used for UltraScale bitstream **on Configuration Packet** level.  
An abstraction layer is necessary when modifying/interpreting the content of registers or the configuration data/logic (frame data).