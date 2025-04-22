`timescale 1ns / 1ps

module return_00 (
    input clka,
    input [10:0] addra,
    output [35:0] douta
    );
    
    assign douta = 36'b0;

endmodule
