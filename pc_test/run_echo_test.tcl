# run_echo_test.tcl -- download and run the lwip_echo_server ELF on the ZedBoard
connect

# Full system reset, which avoids an MMU fault on reload
targets -set -filter {name =~ "APU*"}
rst -system
after 2000

# Program the FPGA with the bitstream
fpga "D:/30-akademik/hft-nn/vivado/hft.runs/impl_1/mlp_system_wrapper.bit"

# PS7 init: bring up the Zynq hardware
targets -set -nocase -filter {name =~ "*A9*#0"}
loadhw -hw "D:/30-akademik/hft-nn/hft-vitis/mlp_platform/export/mlp_platform/hw/mlp_system_wrapper.xsa"
source "D:/30-akademik/hft-nn/hft-vitis/mlp_platform/export/mlp_platform/hw/ps7_init.tcl"
ps7_init
ps7_post_config

# Download and run the ELF
dow "D:/30-akademik/hft-nn/hft-vitis/lwip_echo_server/build/lwip_echo_server.elf"
con
