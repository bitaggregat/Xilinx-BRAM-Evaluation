`timescale 1ns / 1ps

module return_ff (
    input clka,
    input [9:0] addra,
    output [35:0] douta
    );
    
    assign douta = 36'b1;

endmodule