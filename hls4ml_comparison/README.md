# hls4ml comparison

Material behind Section 8 of the paper (Table 12, Fig. 7). The four networks
of Table 4 were generated with hls4ml 1.3.0 for the XC7Z020-1CLG484 at an
8 ns target with Vitis HLS / Vivado 2025.2, Resource strategy, reuse factors
8 to 128. The precision settings reproduce the engine's arithmetic:
`ap_fixed<16,8>` weights and biases, `ap_fixed<40,24>` accumulation,
`ap_fixed<16,8,AP_TRN,AP_SAT>` results.

- `results.csv` – one row per design: HLS worst-case latency and II, post-route
  DSP and LUT, worst negative slack, f_max and latency at f_max. Designs whose
  synthesis exceeds the 53,200 LUTs of the device have `fits = False` and
  synthesis-only DSP/LUT figures.
- `designs/<network>_rf<RF>_resource/` – per design:
  - `hls4ml_config.yml` – full hls4ml configuration
  - `firmware/` – generated top-level HLS source (`nnet_utils` and `ap_types`
    are the stock hls4ml 1.3.0 library and are not repeated here)
  - `mlp_hls_csynth.rpt` – Vitis HLS synthesis report
  - `vivado_synth.rpt` – Vivado synthesis utilization
  - `timing_ooc.tcl`, `timing_ooc.rpt`, `util_ooc.rpt`, `timing_ooc.json` –
    out-of-context place and route with an 8 ns clock constraint, its timing
    and utilization reports, and the extracted summary
  - `summary.json` – HLS and synthesis summary
- `weights/<network>/` – the weights as compiled into the HLS designs,
  identical for every RF of a network.

f_max is computed as 1000 / (8 − WNS) MHz from the post-route worst negative
slack.
