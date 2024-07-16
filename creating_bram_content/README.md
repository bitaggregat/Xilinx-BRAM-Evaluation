# Creating sample BRAM content

A simple python script that helps with filling BRAM blocks.  
The script (```create_sample_bram_content.py```) will create verilog files,  
such as:  

```verilog
 	.INITP_00(256'h646174636173736f72636164696361746e756f63636174756f6261656c626161),
 	.INITP_01(256'h746661746e656d657369747265766461746e656d7473756a64616e6f69746964),
 	.INITP_02(256'h6d6c616c6c61726961746e656d656572676174736e696167616e696167617265),
 	.INITP_03(256'h61656c676e61646e61746e656d6573756d61746e756f6d61676e6f6d6174736f),
 	.INITP_04(256'h61737574617261707061796e61746e61726577736e616c616d696e617972676e),
 	.INITP_05(256'h61796d72616d7261746e656d75677261686372616c61766f72707061656c7070),
 	.INITP_06(256'h727474616e6f69746e6574746174706d657474616b6361747461746173617472),
 	.INITP_07(256'h0a420a656b617761636974616d6f747561797469726f687475616e6f69746361),
 	.INITP_08(256'h736162646e61626c6c616265636e616c61626761626461626b63616279626162),
 	.INITP_09(256'h75616365626c756669747561656265626874616274656b7361626e6973616265),
 	.INITP_0A(256'h6c6c65626665696c6562726f69766168656265726f6665626565626465626573),
 	.INITP_0B(256'h657469627469626874726962647269626e6565777465627972726562746e6562),
 	.INITP_0C(256'h616f6265756c62776f6c62646f6f6c626564616c626b63616c62726574746962),
 	.INITP_0D(256'h746f62746f6f626b6f6f62656e6f62676e696c696f6279646f6274616f626472),
 	.INITP_0E(256'h7262737361726268636e617262656b6172626e69617262796f62786f62656c74),
 	.INITP_0F(256'h6e656b6f72627468676972626567646972626b63697262687461657262646165),
```

Using a known text sample as bram content was very helpful for debugging the hardware design.

## Usage

Example call:  

```bash
python create_test_bram_content.py -a xc7_36k_parity -i sample.txt
```

Calling the script with ```-h``` will print the following:

```bash
usage: create_test_bram_content.py [-h] -i INPUT_FILE [-t {verilog,coe}] [-o OUTPUT_FILE] [-a {xc7_36k,xc7_36k_parity}]

Script that create BRAM template based on text file for debugging purposes.

options:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input_file INPUT_FILE
                        Path to text file that will be used used as bram content
  -t {verilog,coe}, --output_type {verilog,coe}
                        Type of output. Verilog fragment or coe.
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        Path to output file.
  -a {xc7_36k,xc7_36k_parity}, --architecture {xc7_36k,xc7_36k_parity}
                        Type of bram that will be used. Currently only XC7 36K
```

An example text file (```sample.txt```) is already present under this directory.
