module read_bram
#(
	parameter TICKS_PER_BIT = 3472 //400e6/115200
)
(
	input clk_i,
	input uart_rx_i,
	output uart_tx_o,
	output [7:0] led_o
);
	localparam TICKS_PER_BIT_SIZE = $clog2(TICKS_PER_BIT+1);
	
	localparam STATE_WAIT_RX = 4'b0000;
	localparam STATE_SEND = 4'b0001;
	localparam STATE_WAIT = 4'b0011;
	
	reg [3:0] state = STATE_WAIT_RX, next_state = STATE_WAIT_RX;
	reg tx_start;
	reg [7:0] tx_data;
	
	wire fast_clk;
	wire [7:0] rx_data;
	wire rx_done;
	wire tx_done;
	
	assign fast_clk = clk_i;
	
	// state transition
	always @(posedge fast_clk)
	begin
		state <= next_state;
	end
	
	// determine next state
	always @(*)
	begin
		next_state = 4'hx;
		case(state)
		STATE_WAIT_RX:
			if (rx_done && rx_data==8'h73)// received 's'
				next_state = STATE_SEND;
			else
				next_state = STATE_WAIT_RX;
		STATE_SEND:
			next_state = STATE_WAIT;
		STATE_WAIT:
			if (tx_done)
				next_state = STATE_WAIT_RX;
			else
				next_state = STATE_WAIT;
		endcase
	end
	
	// determine output
	always @(posedge fast_clk)
	begin
		tx_data <= tx_data;
		tx_start <= 1'b0;
		case(next_state)
		STATE_WAIT_RX, STATE_WAIT:
			; // defaults
		STATE_SEND:
		begin
			tx_data <= 8'h43;
			tx_start <= 1'b1;
		end
		endcase
    end
    
    uart_rx
    #(
        .TICKS_PER_BIT(TICKS_PER_BIT),
        .TICKS_PER_BIT_SIZE(TICKS_PER_BIT_SIZE)
    ) rx (
        .i_clk(fast_clk),
        .i_enable(1'b1),
        .i_din(uart_rx_i),
        .o_rxdata(rx_data),
        .o_recvdata(rx_done)
    );
    
    uart_tx
    #(
        .TICKS_PER_BIT(TICKS_PER_BIT),
        .TICKS_PER_BIT_SIZE(TICKS_PER_BIT_SIZE)
    ) tx (
        .i_clk(fast_clk),
        .i_start(tx_start),
        .i_data(tx_data),
        .o_done(tx_done),
        .o_dout(uart_tx_o)
    );

endmodule