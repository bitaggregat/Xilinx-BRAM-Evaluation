`timescale 1ns / 1ps
// BRAM replacement module:
// - this is expected to be used as a partial/dynamic configuration module
// - Vivado will use LUTS to implement this module
// - this module is used to "replace" a BRAM in a partial design
//      and thereby deactivating the latter
module return_00 (
    input clka,
    input [9:0] addra,
    output [35:0] douta
    );
    
    assign douta = 36'b0;

endmodule
