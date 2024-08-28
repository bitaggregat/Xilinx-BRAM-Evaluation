`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 2023/07/07 13:29:57
// Design Name: 
// Module Name: new_uart_tx
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


module new_uart_tx(
    input       CLK_50M         ,
    input       rst_n           ,
    input [2:0] bps_sel         ,
    input       check_sel       ,
    input [7:0] din             ,
    input       req             ,
    output      busy            ,
    output reg  TX
    );

    //波特率选择
    // These are adapted to a clock frequency of 400 MHz
    // Change them if clk changes
    localparam  bps9600  = 17'd4_1667;//17'd5208;
    localparam  bps115200 = 17'd3472;
    //波特率计数器
    reg [17:0]  bps_mode;
    reg [17:0]  bps_cnt; //最慢的bps300模式需要18位计数器
    //输入数据缓存
    reg [7:0]   din_reg;
    //线性序列机
    reg         n_cnt_flag;
    reg [3:0]   n_cnt;
    //奇偶校验位
    wire        e_check;
    wire        o_check;
    wire        check;
    //标志是否发送完成
    assign      busy = n_cnt_flag;

    //输入数据寄存
    always@(posedge CLK_50M)	
    if(req)
        din_reg <= din;
    else if(~n_cnt_flag)
        din_reg <= 'd0; 	

    //波特率选择
    always@(*)begin
    case(bps_sel)
        0: bps_mode = bps9600;
        1: bps_mode = bps115200; 
        default : bps_mode = bps9600; 
    endcase
    end  

    //波特率计数器
    always@(posedge CLK_50M or posedge rst_n)
    if(rst_n)
        bps_cnt <= 'd0;
    else if(bps_cnt == bps_mode-1) 
        bps_cnt <= 'd0;
    else 	
        bps_cnt <= bps_cnt + 1'b1;

    //线性序列机
    always@(posedge CLK_50M or posedge rst_n)
    if(rst_n)
        n_cnt_flag <= 1'b0;
    else if(n_cnt == 'd10 && bps_cnt == bps_mode-1)
        n_cnt_flag <= 1'b0; 
    else if(req)
        n_cnt_flag <= 1'b1;

    always@(posedge CLK_50M or posedge rst_n)	
    if(rst_n)
        n_cnt <= 'd0;
    else if(n_cnt_flag) begin
        if(bps_cnt == bps_mode-1)
        n_cnt <= n_cnt + 1'b1;
        else
        n_cnt <= n_cnt; end 
    else
        n_cnt <= 'd0;

    always@(*)begin
    if(n_cnt_flag)
    case(n_cnt)
        0: TX = 1'b1; //此时的波特率不是一个完整的周期，等待进入下一个周期
        1: TX = 1'b0; //start
        2: TX = din_reg[0];
        3: TX = din_reg[1];
        4: TX = din_reg[2];
        5: TX = din_reg[3];
        6: TX = din_reg[4];
        7: TX = din_reg[5];
        8: TX = din_reg[6]; 
        9: TX = din_reg[7];
        //10: TX = check; //校验
        10: TX = 1'b1; //stop
        default TX = 1'b1;
    endcase
    else
        TX = 1'b1; 
    end	

    //奇偶校验
    assign e_check = ^din_reg; //偶校验
    assign o_check = ~e_check; //奇校验

    assign check =(check_sel)? o_check : e_check;//奇偶校验选择

endmodule
