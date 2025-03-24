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
	localparam STATE_SEND_0 = 4'b0001;
	localparam STATE_WAIT_0 = 4'b0011;
	localparam STATE_SEND_1 = 4'b0010;
	localparam STATE_WAIT_1 = 4'b0110;
	localparam STATE_SEND_2 = 4'b0111;
	localparam STATE_WAIT_2 = 4'b0101;
	localparam STATE_SEND_3 = 4'b0100;
	localparam STATE_WAIT_3 = 4'b1100;
	localparam STATE_SEND_PAR = 4'b1101;
	localparam STATE_WAIT_PAR = 4'b1111;
	
	reg [3:0] state = STATE_WAIT_RX, next_state = STATE_WAIT_RX;
	reg tx_start;
	reg [7:0] tx_data;
	reg [35:0] batch_data;
	
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
				next_state = STATE_SEND_0;
			else
				next_state = STATE_WAIT_RX;
		STATE_SEND_0:
			next_state = STATE_WAIT_0;
		STATE_WAIT_0:
			if (tx_done)
				next_state = STATE_SEND_1;
			else
				next_state = STATE_WAIT_0;
		STATE_SEND_1:
			next_state = STATE_WAIT_1;
		STATE_WAIT_1:
			if (tx_done)
				next_state = STATE_SEND_2;
			else
				next_state = STATE_WAIT_1;
		STATE_SEND_2:
			next_state = STATE_WAIT_2;
		STATE_WAIT_2:
			if (tx_done)
				next_state = STATE_SEND_3;
			else
				next_state = STATE_WAIT_2;
		STATE_SEND_3:
			next_state = STATE_WAIT_3;
		STATE_WAIT_3:
			if (tx_done)
				next_state = STATE_SEND_PAR;
			else
				next_state = STATE_WAIT_3;
		STATE_SEND_PAR:
			next_state = STATE_WAIT_PAR;
		STATE_WAIT_PAR:
			if (tx_done)
				next_state = STATE_WAIT_RX;
			else
				next_state = STATE_WAIT_PAR;
		endcase
	end
	
	// determine output
	always @(posedge fast_clk)
	begin
		tx_data <= tx_data;
		tx_start <= 1'b0;
		batch_data <= 36'hcafebeaf7;
		case(next_state)
		STATE_WAIT_RX, STATE_WAIT_0, STATE_WAIT_1, STATE_WAIT_2, STATE_WAIT_3, STATE_WAIT_PAR:
			; // defaults
		STATE_SEND_0:
		begin
			tx_data <= batch_data[7:0];
			tx_start <= 1'b1;
		end
		STATE_SEND_1:
		begin
			tx_data <= batch_data[15:8];
			tx_start <= 1'b1;
		end
		STATE_SEND_2:
		begin
			tx_data <= batch_data[23:16];
			tx_start <= 1'b1;
		end
		STATE_SEND_3:
		begin
			tx_data <= batch_data[31:24];
			tx_start <= 1'b1;
		end
		STATE_SEND_PAR:
		begin
			tx_data <= {4'h00, batch_data[35:32]};
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