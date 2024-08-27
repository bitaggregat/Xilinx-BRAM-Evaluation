## Measured Stats

### XC7 Measurements

Measurements on XC7 devices were currently only done on the Basys3.

#### Basys3 (xc7a35tcpg236-1) Measurements

These measurements were done on our local basys3 board. (sticker on the downside of the board: **DA89AC3**).  
Measurements were done on:

- 3 x 36K BRAM Blocks
- All 3 BRAM Blocks were within the same row of the FPGA
- Parity and Data bits were used
- Each BRAM Block was measured 4 times (named Read 1, Read 2 ...)
- "-" stands for "no bitlfip"
- Indexes of data in bram are measured in **bytes**

|Tile and Slice|BRAM value before power outage|% of flipped bits in data|% of flipped bits in parity|other|
|--------------|------------------------------|---------------------------|---------------------------|-----|
|BRAM_X30Y35_RAMB_X1Y6|ff|0|0|-|
|BRAM_X30Y35_RAMB_X1Y6|00|0.00024606299212598425|0|-|
|BRAM_X30Y35_RAMB_X1Y7|ff|0|0|-|
|BRAM_X30Y35_RAMB_X1Y7|00|0.0002768208661417323|0|-|
|BRAM_X30Y35_RAMB_X1Y8|ff|0|0|-|
|BRAM_X30Y35_RAMB_X1Y8|00|0.00024606299212598425|0|-|
|BRAM_X30Y35_RAMB_X1Y6|00|~0.005580357142857143|0|initializing BRAM without values 100 times consecutively|

#### BRAM_X30Y35_RAMB_X1Y6 (previous value 00)

|Byte Position|Read 1|Read 2|Read 3|Read 4|
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

#### BRAM_X30Y35_RAMB_X1Y7 (previous value 00)

|Byte Position|Read 1 |All other Reads|
|-|-|-|
|131|40|40|
|419|c0|c0|
|1523|40|40|
|3007|80|80|
|3438|**82**|80|
|4095|c0|c0|

#### BRAM_X30Y35_RAMB_X1Y8 (previous value 00)

|Byte Position|Read 1|Read 2|Read 3|Read 4|
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

### XCUS+ Measurements

#### te0802 Measurements

- WIP

## Observations

### XC7 Observations

- The amount of flipped bits is low on the basys3. This is in accordance with newer generation zed boards mentioned in the paper.
- Tests were also repeated once with a heat gun
- Tests were also repeated using a wait time of 30 seconds.
- Neither temperature change nor increased wait time had an influence on the amount of flipped bits
- Flashing the partial bitstream that reactivates the bram (without initializing it's values) multiple times increases the amount of flipped bits by a great amount
- Flashing the partial bitstream multiples times was not mentioned in the paper and could be a new insight.
- Flipped bits seem very volatile (this became very clear during ticket review)

#### <a name="link1"></a> Initializing BRAM without values multiple times

- The amount of flipped bits increased alot by doing this
- We looked at the flipped bits from a **byte level** perspective
- But the flipped **bytes** were predictable
- e.g. flashing 100 times led to many ```c0```, ```80``` and ```40```'s
- flasing 1000 times led to more variety in flipped bytes (e.g ```01```, ```41```, ```82```)
- There seems to be a correlation between amount of times the bram was activated and randomness of the bram content

### XCUS+ Observations

WIP