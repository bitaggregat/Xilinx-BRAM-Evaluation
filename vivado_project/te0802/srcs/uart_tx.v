/*
MIT License

Copyright (c) 2020 Clemens Fritzsch

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

module uart_tx
#(
	parameter CLK_PER_BIT = 1250,	// 12 MHz clock, 9600 baud
	parameter CLK_COUNTER_LENGTH = $clog2(CLK_PER_BIT+1)
)
(
	input clk, 
	input [7:0] data, 
	input tx_start, 
	output reg tx, 
	output reg tx_done
);
	
	localparam STATE_IDLE = 3'h0;
	localparam STATE_START_BIT = 3'h1;
	localparam STATE_DATA_BITS = 3'h2;
	localparam STATE_STOP_BIT = 3'h3;
	localparam STATE_DONE = 3'h4;
	
	reg [2:0] state = STATE_IDLE;
	reg [CLK_COUNTER_LENGTH-1:0] clk_counter;
	reg [7:0] data_buf;
	reg [3:0] bit_counter;
	
	always @(posedge clk)
	begin
		case (state)
		STATE_IDLE:
		begin
			tx <= 1'b1;
			tx_done <= 1'b0;
			if (tx_start)
			begin
				data_buf <= data;
				state <= STATE_START_BIT;
				clk_counter <= 0;
			end
		end
		STATE_START_BIT:
		begin
			tx <= 1'b0;
			if (clk_counter < CLK_PER_BIT-1)
			begin
				clk_counter <= clk_counter + 1;
			end
			else
			begin
				state <= STATE_DATA_BITS;
				bit_counter <= 4'b0;
				clk_counter <= 0;
			end
		end
		STATE_DATA_BITS:
		begin
			tx <= data_buf[0];
			if (clk_counter < CLK_PER_BIT-1)
			begin
				clk_counter <= clk_counter + 1;
			end
			else
			begin
				if (bit_counter < 7)
				begin
					data_buf <= data_buf >> 1;
					bit_counter <= bit_counter + 1;
					clk_counter <= 0;
				end
				else
				begin
					state <= STATE_STOP_BIT;
					clk_counter <= 0;
				end
			end
		end
		STATE_STOP_BIT:
		begin
			tx <= 1'b1;
			if (clk_counter < CLK_PER_BIT-1)
			begin
				clk_counter <= clk_counter + 1;
			end
			else
			begin
				state <= STATE_DONE;
			end
		end
		STATE_DONE:
		begin
			tx <= 1'b1;
			tx_done <= 1'b1;
			state <= STATE_IDLE;
		end
		default:
		begin
			// reset
			tx <= 1'b1;
			tx_done <= 1'b0;
			data_buf <= 8'b0;
			clk_counter <= 0;
			state <= STATE_IDLE;
		end
		endcase
	end
endmodule
