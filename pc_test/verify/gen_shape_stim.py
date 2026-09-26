#!/usr/bin/env python3
"""
Stimulus for mlp_shape_tb.vhd: run-time shape reconfiguration.

For each of the four verification networks, in one continuous simulation and
without a reset in between:
  1. write the per-layer width registers (0x10..0x1C) with the network's REAL
     shape (no truncation to the old fixed 64-32-16-3 layout),
  2. load weights and biases with the same address scheme as
     mlp_weight_loader.h, using the real per-layer input counts,
  3. stream N input vectors and check every output against a bit-exact
     reference computed on the real, untruncated network,
  4. check the cycle counter against the analytic model
     sum_l (ceil(n_l/3) + 14).

The reference here is deliberately independent of verify_bitexact._pad, which
clips every network to 64-32-16-3 and therefore cannot detect a truncation.

Output file format (one record per line):
  L <text>                     label
  W <addr> <value>             AXI-Lite write
  V <x0> ... <x63>             input vector (Q8.8 int16)
  E <o0> <o1> <o2> <cycles>    expected outputs and cycle count
"""
import argparse
import os
import zipfile

import numpy as np

import verify_bitexact as vb

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = [
    "mlp_40_64_32_16_3_bfdb6941.pth",
    "mlp_40_64_64_32_3_7e3943ab.pth",
    "mlp_40_32_16_8_3_fa8bb051.pth",
    "mlp_40_10_16_8_3_1421e245.pth",
]


def real_layers(path):
    """Quantised (W, b) per layer with their true shapes, firmware rounding."""
    z = zipfile.ZipFile(path)
    items = sorted((i for i in z.infolist() if "/data/" in i.filename),
                   key=lambda i: int(i.filename.split("/")[-1]))
    arrs = [np.frombuffer(z.read(i.filename), dtype="<f4") for i in items]
    out = []
    for k in range(0, len(arrs), 2):
        W, b = arrs[k], arrs[k + 1]
        W = W.reshape(b.size, W.size // b.size)
        out.append((np.trunc(W * np.float32(256)).astype(np.int64),
                    np.trunc(b * np.float32(256)).astype(np.int64)))
    return out


def forward_real(x64, layers):
    """Bit-exact mlp_engine arithmetic on the real network shape."""
    a = x64
    for li, (W, B) in enumerate(layers):
        acc = a[:, :W.shape[1]] @ W.T + (B << 8)
        s = np.clip(acc >> 8, -32768, 32767)
        if li < len(layers) - 1:
            s = np.maximum(s, 0)
        a = s
    return a


def cycles(layers):
    return sum((W.shape[0] + 2) // 3 + 14 for W, _ in layers)


def load_writes(layers):
    """AXI writes of mlp_weight_loader.h load_layer_to_hw, real shapes."""
    wr = []
    base = 0
    for W, B in layers:
        n_out, n_in = W.shape
        for k in range((n_out + 2) // 3):
            word = base + k
            for n in range(3):
                j = 3 * k + n
                for i in range(64):
                    v = int(W[j, i]) if (j < n_out and i < n_in) else 0
                    wr.append((0x20000 + (n * 64 + i) * 512 + word * 4, v))
                bias = int(B[j]) if j < n_out else 0
                wr.append((0x20000 + (192 + n) * 512 + word * 4, bias))
        base += (n_out + 2) // 3
    return wr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=50, help="vectors per network")
    ap.add_argument("--out", default=os.path.join(HERE, "shape_stim.txt"))
    args = ap.parse_args()

    x = vb.parse_stream(os.path.join(HERE, "verify_stream.csv"), 20000, saturating=True)
    rng = np.random.default_rng(1)
    with open(args.out, "w") as f:
        for m in MODELS:
            layers = real_layers(os.path.join(HERE, "models", m))
            shape = [W.shape[0] for W, _ in layers]
            f.write(f"L {m} shape 40-{'-'.join(map(str, shape))} "
                    f"cycles {cycles(layers)}\n")
            for reg, n in zip((0x10, 0x14, 0x18, 0x1C), shape):
                f.write(f"W {reg} {n}\n")
            for a, v in load_writes(layers):
                f.write(f"W {a} {v}\n")
            idx = rng.choice(len(x), args.n, replace=False)
            y = forward_real(x[idx], layers)
            for r in range(args.n):
                f.write("V " + " ".join(str(int(t)) for t in x[idx[r]]) + "\n")
                # The on-chip counter reads one less than eq. (1): it counts
                # non-idle cycles (paper, Section 5.7).
                f.write(f"E {y[r, 0]} {y[r, 1]} {y[r, 2]} {cycles(layers) - 1}\n")
            print(m, "shape", shape, "cycles", cycles(layers))
    print("yazildi:", args.out)


if __name__ == "__main__":
    main()
