# Bitstream Handling

This directory contains a python library that can handle Xilinx 7 Series Bitstreams and F4PGA FASMs.
The code was orignally written for another Open Source project.  
Small relics, such as variable naming conventions may still be present in the code.  

The code also contains a python wrapper for a modified version of openFPGALoader.  
openFPGALoader is an open source tool for FPGA bitstream flash operations.  
The source code of the modified openFPGALoader version was not included in this repository, as it would be too big.  
TODO: Mirror openFPGALoader and reproduce modifications done to support partial bistreams  
Instead a binary of the modified openFPGALoader is currently available under ```copenFPGALoader/```.

**Note**: [See openFPGALoaders install instructions](https://trabucayre.github.io/openFPGALoader/guide/install.html) if theres any missing dependencies for copenFPGALoader.
