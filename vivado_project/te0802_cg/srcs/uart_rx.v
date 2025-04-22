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

module uart_rx
#(
	// CLK_PER_BIT has to be at least 2 or STATE_START_BIT has to be skipped
	parameter CLK_PER_BIT = 1250,	// 12 MHz clock, 9600 baud
	parameter CLK_COUNTER_LENGTH = $clog2(CLK_PER_BIT+1)
)
(
	input clk, 
	input rx,
	output reg [7:0] data,
	output reg rx_done
	//output [2:0] out_state
);
	
	localparam STATE_IDLE = 3'b000;
	localparam STATE_START_BIT = 3'b001;
	localparam STATE_DATA_BITS = 3'b011;
	localparam STATE_STOP_BIT = 3'b010;
	localparam STATE_DONE = 3'b110;
	
	reg [2:0] state = STATE_IDLE;
	reg [CLK_COUNTER_LENGTH-1:0] clk_counter;
	reg [7:0] data_buf;
	reg rx_buf;
	//reg [3:0] rx_buf_extension;
	reg [3:0] bit_counter;
	
	//assign out_state = state; 
	
	// use register for input since it's an clock domain crossing
	always @(posedge clk)
	begin
		//rx_buf_extension <= {rx_buf_extension[2:0], rx};
	    rx_buf <= rx;//_buf_extension[3];
	end
	
	always @(posedge clk)
	begin
		case (state)
		STATE_IDLE:
		begin
			rx_done <= 1'b0;
			if (rx_buf == 1'b0)
			begin
				state <= STATE_START_BIT;
				clk_counter <= 1; // we want to count clk cycles, but it takes one cycle to start counting
			end
		end
		STATE_START_BIT:
		begin
			// wait for half bit duration
			// so the data bits are always determined in the middle of the signal
			if (clk_counter < CLK_PER_BIT/2-1)
			begin
				clk_counter <= clk_counter + 1;
			end
			else if (rx_buf == 1'b0) // check start bit again to reduce errors by noise
			begin
				state <= STATE_DATA_BITS;
				bit_counter <= 4'b0;
				clk_counter <= 1;
			end
			else
			begin
				// assume noise caused initial start bit and ignore it
				state <= STATE_IDLE;
			end
			
		end
		STATE_DATA_BITS:
		begin
			// wait for next bit
			if (clk_counter < CLK_PER_BIT-1)
			begin
				clk_counter <= clk_counter + 1;
			end
			else 
			begin
				data_buf <= {rx_buf, data_buf[7:1]};
				clk_counter <= 0;
				if (bit_counter < 7)
				begin
					bit_counter <= bit_counter + 1;
				end
				else
				begin
					state <= STATE_STOP_BIT;
				end
			end
		end
		STATE_STOP_BIT:
		begin
			// wait for stop bit
			if (clk_counter < CLK_PER_BIT-1)
			begin
				clk_counter <= clk_counter + 1;
			end
			else if (rx_buf == 1'b1)
			begin
				// data successful received
				data <= data_buf;
				state <= STATE_DONE;
			end
			else
			begin
				// stop bit not found -> ignore transfered data
				state <= STATE_IDLE;
			end
		end
		STATE_DONE:
		begin
			// use extra state for tx_done to be sure that data is stable
			// else we might see metastable data values when triggering on posedge rx_done
				rx_done <= 1'b1;
				state <= STATE_IDLE;
		end
		default
		begin
			rx_done <= 1'b0;
			data_buf <= 8'b0;
			clk_counter <= 0;
			bit_counter <= 3'h0;
			state <= STATE_IDLE;
			
		end
		endcase
	end
	
endmodule
