`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03/24/2025 12:20:51 PM
// Design Name: 
// Module Name: tb_read_bram
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module tb_read_bram(

    );
    
    localparam T=2;
    localparam TICKS_PER_BIT = 4;
    localparam TICKS_PER_BIT_SIZE = $clog2(TICKS_PER_BIT+1);
    
    
    reg clk;
    
    wire uart_rx;
    reg to_dut_start;
    reg [7:0] to_dut_data;
    wire to_dut_done;
    
    wire uart_tx;
    wire [7:0] from_dut_data;
    wire from_dut_done;
    
    wire [7:0] led;
    
    read_bram
    #(
        .TICKS_PER_BIT(TICKS_PER_BIT)
    ) dut (
        .clk_i(clk),
        .uart_rx_i(uart_rx),
        .uart_tx_o(uart_tx),
        .led_o(led)
    );
    
    uart_tx 
	#(
        .TICKS_PER_BIT(TICKS_PER_BIT),
        .TICKS_PER_BIT_SIZE(TICKS_PER_BIT_SIZE)
    ) uart_to_dut (
        .i_clk(clk),
        .i_start(to_dut_start),
        .i_data(to_dut_data),
        .o_done(to_dut_done),
        .o_dout(uart_rx)     
    );
    
    uart_rx
	#(
        .TICKS_PER_BIT(TICKS_PER_BIT),
        .TICKS_PER_BIT_SIZE(TICKS_PER_BIT_SIZE)
    ) uart_from_dut (
        .i_clk(clk),
        .i_enable(1'b1),
        .i_din(uart_tx),
        .o_rxdata(from_dut_data),
        .o_recvdata(from_dut_done)
    );
    

    always
    begin
        clk = 1'b1;
        #(T/2);
        clk = 1'b0;
        #(T/2);
    end
    
    /*
    task wait_busy_timeout;
    begin
        fork: wait_timeout
        begin
            wait(busy == 1'b0);
            disable wait_timeout;
        end
        begin
            #(16*TICKS_PER_BIT) $display("ERROR: timeout for transmission of value 0x%x", expected);
            $finish;
        end
        join
    end
    endtask
    */
    
    initial
    begin
        // send u
        to_dut_data = 8'h40;
        @(negedge clk);
        to_dut_start = 1'b1;
        @(negedge clk);
        to_dut_start = 1'b0;
        @(posedge to_dut_done);
        
        // nothing should happen
        fork: wait_nothing
        begin
            wait(uart_tx == 1'b0);
            $display("ERROR: unknown command triggered submission");
            $finish;
        end
        begin
            #(14*T*TICKS_PER_BIT);
            disable wait_nothing;
        end
        join
        
        // send s
        to_dut_data = 8'h73;
        @(negedge clk);
        to_dut_start = 1'b1;
        @(negedge clk);
        to_dut_start = 1'b0;
        @(posedge to_dut_done);
        
        // receive
        fork: wait_receive
        begin
            wait(from_dut_done == 1'b1);
            disable wait_receive;
        end
        begin
            #(14*T*TICKS_PER_BIT) $display("ERROR: expected submission missing");
            $finish;
        end
        join
        
        @(negedge clk);
        if (from_dut_data == 8'h43)
            $display("PASSED");
        else
            $display("ERROR: wrong value received 0x%x", from_dut_data);
        
        @(negedge clk);
        @(negedge clk);
        $finish;
    end


endmodule
