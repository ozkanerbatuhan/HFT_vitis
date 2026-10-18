#ifndef DEFINES_H_
#define DEFINES_H_

#include "ap_fixed.h"
#include "ap_int.h"
#include "nnet_utils/nnet_types.h"
#include <array>
#include <cstddef>
#include <cstdio>
#include <tuple>
#include <tuple>


// hls-fpga-machine-learning insert numbers

// hls-fpga-machine-learning insert layer-precision
typedef ap_fixed<16,8> input_t;
typedef ap_fixed<40,24> _0_accum_t;
typedef ap_fixed<16,8,AP_TRN,AP_SAT,0> layer2_t;
typedef ap_fixed<16,8> _0_weight_t;
typedef ap_fixed<16,8> _0_bias_t;
typedef ap_uint<1> layer2_index;
typedef ap_fixed<16,8,AP_TRN,AP_SAT,0> layer3_t;
typedef ap_fixed<18,8> _1_table_t;
typedef ap_fixed<40,24> _2_accum_t;
typedef ap_fixed<16,8,AP_TRN,AP_SAT,0> layer4_t;
typedef ap_fixed<16,8> _2_weight_t;
typedef ap_fixed<16,8> _2_bias_t;
typedef ap_uint<1> layer4_index;
typedef ap_fixed<16,8,AP_TRN,AP_SAT,0> layer5_t;
typedef ap_fixed<18,8> _3_table_t;
typedef ap_fixed<40,24> _4_accum_t;
typedef ap_fixed<16,8,AP_TRN,AP_SAT,0> layer6_t;
typedef ap_fixed<16,8> _4_weight_t;
typedef ap_fixed<16,8> _4_bias_t;
typedef ap_uint<1> layer6_index;
typedef ap_fixed<16,8,AP_TRN,AP_SAT,0> layer7_t;
typedef ap_fixed<18,8> _5_table_t;
typedef ap_fixed<40,24> _6_accum_t;
typedef ap_fixed<16,8,AP_TRN,AP_SAT,0> result_t;
typedef ap_fixed<16,8> _6_weight_t;
typedef ap_fixed<16,8> _6_bias_t;
typedef ap_uint<1> layer8_index;

// hls-fpga-machine-learning insert emulator-defines


#endif
