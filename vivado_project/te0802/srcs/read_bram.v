`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 2023/07/07 20:07:11
// Design Name: 
// Module Name: read_bram
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: Read one block RAM's memory, RAM config: 8*2k
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////

module read_bram(
    input           sys_clk_p,
    input           rst,
    input           uart_rxd,
    output          uart_txd,
    output [7:0]    led
    );
    /*****************************Parameter*********************************/
    parameter   WRITE_DEPTH =   4096 / 4;

    /*****************************Register*********************************/
    reg         r_uart_enable   ;
    reg         r_bram_flag     ;
    reg [1:0]   r_bram_cnt      ;  // BRAM have 2 cycles' latency, wait one more cycle for robustness
    reg [9:0]   r_bram_addr     ;
    reg [3:0]   count_in_batch  ;
    reg [1:0]   r_exec_state    ;
    reg [1:0]   r_next_state    ;
    reg [7:0]   r_bram_dout     ;
    reg [7:0]   r_led           ;
    reg         batch_done      ;
    reg [35:0]  bram_batch      ;

    /*****************************Wire************************************/
    wire        w_clk           ;
    wire        w_resetn        ;
    wire        w_uart_busy     ;
    wire [35:0] w_bram_dout     ;
    wire [7:0]  w_uart_txdata   ;
    wire        rx_received     ;
    wire        send_enable     ;

    /*************************Combinational Logic************************/
    assign w_resetn         =   ~rst                    ;
    assign w_uart_txdata    =   r_bram_dout             ;
    assign led              =   r_led                   ;
    assign send_enable      =   1'b1                    ;

    /****************************Processing*****************************/
    always @(posedge w_clk) begin
        if(w_resetn || rx_received) begin
            r_exec_state <= IDLE;
        end else begin
            r_exec_state <= r_next_state;
        end
    end

    /*******************************FSM************************************/
    parameter   IDLE = 2'b00,
                READ = 2'b01,
                SEND = 2'b10,
                NEXT = 2'b11;
                
    parameter   NO_RESET = 1'b0,
                RESETTING = 1'b1;
    parameter TICKS_PER_BIT        = 35;
    parameter TICKS_PER_BIT_SIZE   = 12;
                
    
    always@(posedge w_clk)begin
    case(r_exec_state)
        IDLE: r_next_state = send_enable ? READ : IDLE;
        READ: r_next_state = (r_bram_flag&&r_bram_cnt==2'd2) ? SEND : READ;
        SEND: r_next_state = NEXT;
        NEXT: r_next_state = (r_bram_addr==WRITE_DEPTH) ? IDLE : (w_uart_busy ? NEXT : (batch_done ? READ : SEND));
        default: r_next_state = IDLE;
    endcase
    end

    always@(posedge w_clk)begin
    case(r_exec_state)
        IDLE: begin
            r_led <= 8'b10000000;
            r_bram_addr <= 9'd0;
            r_bram_flag <= 1'b0;
            count_in_batch <= 1'd0;
            r_uart_enable <= 1'b0;
            r_bram_cnt <= 2'd0;
        end
        READ: begin
            r_led <= 8'b01000000;
            if(!r_bram_flag)begin
                r_bram_flag <= 1'b1;
                r_bram_cnt <= 2'd0;
                batch_done <= 1'b0;
            end else if(r_bram_cnt==2'd2)begin
                r_bram_flag <= 1'b0;
                bram_batch <= w_bram_dout;
            end else begin
                r_bram_cnt <= r_bram_cnt + 2'd1;
            end
        end
        SEND: begin
            r_led <= 8'b11000000;
            r_uart_enable <= 1'b1;
            // Custom protocol
            // Helps us knowing where first byte of bram starts
            case(count_in_batch)
                0: r_bram_dout <= {6'b0, r_bram_addr[9:8]};    // index of data byte 1
                1: r_bram_dout <= r_bram_addr[7:0];             // index of data byte 2
                2: r_bram_dout <= 8'h3b;                        // delimiter character
                3: r_bram_dout <= bram_batch[7:0];              // data byte 1
                4: r_bram_dout <= bram_batch[15:8];             // data byte 2
                5: r_bram_dout <= bram_batch[23:16];            // data byte 3
                6: r_bram_dout <= bram_batch[31:24];            // data byte 4
                7: r_bram_dout <= {4'b0000, bram_batch[35:32]}; // filler + 4 parity bits
            endcase
            if(count_in_batch == 7)begin
                batch_done <= 1'b1;
            end
        end
        NEXT: begin
            r_led <= 8'b00100000;
            if(r_bram_addr!=WRITE_DEPTH && !w_uart_busy && batch_done)begin
                // Case:
                // Data and parity byte have been send,
                // -> Increase bram addr
                r_uart_enable <= 1'b0;
                count_in_batch <= 1'd0;
                r_bram_addr <= r_bram_addr + 1;
            end else if (r_bram_addr!=WRITE_DEPTH && !w_uart_busy)begin
                // Case:
                // Not all bytes have been send
                count_in_batch <= count_in_batch + 1;
                r_uart_enable <= 1'b0;
            end else begin
                r_uart_enable <= r_uart_enable;
                r_bram_addr <= r_bram_addr;
            end
        end
        default: r_led <= 8'b00000000;
    endcase
    end

    /****************************Instanation*****************************/
    clk_wiz_0 clock
    (
        .clk_out1(w_clk),
        .clk_in1(sys_clk_p)
    );
        
    new_uart_tx new_uart(
        .CLK_50M(w_clk),  
        .rst_n(w_resetn),   
        .bps_sel(3'd1),     // 9600, DONT CHANGE
        .check_sel(1'b0),   // Even
        .din(w_uart_txdata),      
        .req(r_uart_enable),
        .busy(w_uart_busy),
        .TX(uart_txd)
    );
    
    uart_rx 
    #(
		.TICKS_PER_BIT(TICKS_PER_BIT),
		.TICKS_PER_BIT_SIZE(TICKS_PER_BIT_SIZE)
	) rx (	
		.i_clk(w_clk),
		.i_din(uart_rxd),
		.i_enable(1'b1),
		.o_recvdata(rx_received)
	);


    bram_read_test bram_wrap(
    .clka(w_clk),
    .addra(r_bram_addr),
    .douta(w_bram_dout) 
    );

endmodule