
create_project -in_memory -part xc7z020clg484-1
add_files [glob {D:/hls_prj/40-64-64-32-3_rf128_resource/mlp_hls_prj/solution1/syn/verilog/*}]
synth_design -top mlp_hls -part xc7z020clg484-1 -mode out_of_context
create_clock -period 8.0 -name ap_clk [get_ports ap_clk]
opt_design
place_design
route_design
report_timing_summary -max_paths 3 -file {D:/hls_prj/40-64-64-32-3_rf128_resource/timing_ooc.rpt}
report_utilization -file {D:/hls_prj/40-64-64-32-3_rf128_resource/util_ooc.rpt}
