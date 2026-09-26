/*
 * host_loader_check.c
 *
 * Runs the firmware's shaped-model loader (mlp_weight_loader.h, unmodified) on
 * the PC against a .shp file and prints every AXI-Lite write it would issue,
 * as "W <addr> <value>". Comparing this with the write sequence that passed
 * the RTL simulation (gen_shape_stim.py) checks the packet format and the C
 * loader without a board.
 *
 * Build: gcc -O1 -I. -Ishim host_loader_check.c -o host_loader_check -lm
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

/* Shim for the two Xilinx headers the loader pulls in. */
typedef uint32_t u32;
static void mlp_write_reg(u32 offset, u32 value) {
    printf("W %u %d\n", offset, (int)(int32_t)value);
}
#define MLP_DRIVER_H
#define XIL_IO_H

#include "../../lwip_echo_server/src/mlp_weight_loader.h"

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: %s model.shp\n", argv[0]); return 2; }
    FILE *f = fopen(argv[1], "rb");
    if (!f) { perror(argv[1]); return 2; }
    static unsigned char pkt[1 << 17];
    size_t len = fread(pkt, 1, sizeof(pkt), f);
    fclose(f);

    /* Same parsing as the 'S' case in main.c */
    uint32_t dims[5];
    if (len < 4 + sizeof(dims) || pkt[0] != 'S') { fprintf(stderr, "bad header\n"); return 1; }
    memcpy(dims, pkt + 4, sizeof(dims));
    int n_in = (int)dims[0];
    int n[4] = { (int)dims[1], (int)dims[2], (int)dims[3], (int)dims[4] };
    int nf = shaped_model_floats(n_in, n);
    if (len < 4 + sizeof(dims) + nf * sizeof(float)) { fprintf(stderr, "short\n"); return 1; }
    static float blob[64*64*3 + 64*3 + 3*64 + 3];
    memcpy(blob, pkt + 4 + sizeof(dims), nf * sizeof(float));
    return load_shaped_network(n_in, n, blob) == 0 ? 0 : 1;
}
