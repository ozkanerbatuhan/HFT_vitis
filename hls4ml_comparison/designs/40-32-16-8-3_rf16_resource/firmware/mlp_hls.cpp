#include <iostream>

#include "mlp_hls.h"
#include "parameters.h"


void mlp_hls(
    input_t input_1[40],
    result_t layer8_out[3]
) {

    // hls-fpga-machine-learning insert IO
    #pragma HLS ARRAY_RESHAPE variable=input_1 complete dim=0
    #pragma HLS ARRAY_PARTITION variable=layer8_out complete dim=0
    #pragma HLS INTERFACE ap_vld port=input_1,layer8_out 
    #pragma HLS DATAFLOW

    // hls-fpga-machine-learning insert load weights
#ifndef __SYNTHESIS__
    static bool loaded_weights = false;
    if (!loaded_weights) {
        nnet::load_weights_from_txt<_0_weight_t, 1280>(w2, "w2.txt");
        nnet::load_weights_from_txt<_0_bias_t, 32>(b2, "b2.txt");
        nnet::load_weights_from_txt<_2_weight_t, 512>(w4, "w4.txt");
        nnet::load_weights_from_txt<_2_bias_t, 16>(b4, "b4.txt");
        nnet::load_weights_from_txt<_4_weight_t, 128>(w6, "w6.txt");
        nnet::load_weights_from_txt<_4_bias_t, 8>(b6, "b6.txt");
        nnet::load_weights_from_txt<_6_weight_t, 24>(w8, "w8.txt");
        nnet::load_weights_from_txt<_6_bias_t, 3>(b8, "b8.txt");
        loaded_weights = true;    }
#endif
    // ****************************************
    // NETWORK INSTANTIATION
    // ****************************************

    // hls-fpga-machine-learning insert layers

    layer2_t layer2_out[32];
    #pragma HLS ARRAY_PARTITION variable=layer2_out complete dim=0

    layer3_t layer3_out[32];
    #pragma HLS ARRAY_PARTITION variable=layer3_out complete dim=0

    layer4_t layer4_out[16];
    #pragma HLS ARRAY_PARTITION variable=layer4_out complete dim=0

    layer5_t layer5_out[16];
    #pragma HLS ARRAY_PARTITION variable=layer5_out complete dim=0

    layer6_t layer6_out[8];
    #pragma HLS ARRAY_PARTITION variable=layer6_out complete dim=0

    layer7_t layer7_out[8];
    #pragma HLS ARRAY_PARTITION variable=layer7_out complete dim=0

    nnet::dense<input_t, layer2_t, config2>(input_1, layer2_out, w2, b2); // _0

    nnet::relu<layer2_t, layer3_t, relu_config3>(layer2_out, layer3_out); // _1

    nnet::dense<layer3_t, layer4_t, config4>(layer3_out, layer4_out, w4, b4); // _2

    nnet::relu<layer4_t, layer5_t, relu_config5>(layer4_out, layer5_out); // _3

    nnet::dense<layer5_t, layer6_t, config6>(layer5_out, layer6_out, w6, b6); // _4

    nnet::relu<layer6_t, layer7_t, relu_config7>(layer6_out, layer7_out); // _5

    nnet::dense<layer7_t, result_t, config8>(layer7_out, layer8_out, w8, b8); // _6

}

