#!/usr/bin/env python3
"""
Convert a PyTorch MLP checkpoint into a shaped model packet (.shp).

Unlike the fixed '.bin' template (64-32-16-3, anything larger is truncated),
the .shp file carries the network's real shape, and the firmware writes the
per-layer width registers of the engine to match. The file is the complete
UDP packet ('S' command) and is sent unchanged by hft_engine_linux.

Layout (little endian):
  byte 0      'S'
  bytes 1..3  0
  u32 x 5     n_in, n1, n2, n3, n4
  float32[]   W1 B1 W2 B2 W3 B3 W4 B4, each W row-major [n_out x n_in]

Hardware bounds: n_in <= 64, every layer <= 64 neurons, n4 == 3.

Usage:  python shaped_model.py model.pth [out.shp]
"""
import struct
import sys
import zipfile

import numpy as np

MAX_WIDTH = 64
N_OUTPUTS = 3


def read_layers(pth_path):
    """(W, b) float32 pairs in file order, straight from the .pth zip.

    Reads the zip directly so that torch is not needed; parameter tensors are
    stored in order under <archive>/data/<k>.
    """
    z = zipfile.ZipFile(pth_path)
    items = sorted((i for i in z.infolist() if "/data/" in i.filename),
                   key=lambda i: int(i.filename.split("/")[-1]))
    arrs = [np.frombuffer(z.read(i.filename), dtype="<f4") for i in items]
    if len(arrs) % 2:
        raise ValueError("expected weight/bias pairs")
    layers = []
    for k in range(0, len(arrs), 2):
        W, b = arrs[k], arrs[k + 1]
        layers.append((W.reshape(b.size, W.size // b.size), b))
    return layers


def check_shape(layers):
    if len(layers) != 4:
        raise ValueError(f"hardware runs exactly 4 layers, model has {len(layers)}")
    n_in = layers[0][0].shape[1]
    prev = n_in
    for i, (W, b) in enumerate(layers):
        if W.shape[1] != prev:
            raise ValueError(f"layer {i+1} expects {W.shape[1]} inputs, gets {prev}")
        prev = W.shape[0]
    shape = [W.shape[0] for W, _ in layers]
    if n_in > MAX_WIDTH or any(n > MAX_WIDTH for n in shape) or shape[-1] != N_OUTPUTS:
        raise ValueError(f"shape {n_in}-{'-'.join(map(str, shape))} outside hardware bounds "
                         f"(<= {MAX_WIDTH} per layer, {N_OUTPUTS} outputs)")
    return n_in, shape


def to_packet(layers):
    n_in, shape = check_shape(layers)
    body = b"".join(W.astype("<f4").tobytes() + b.astype("<f4").tobytes()
                    for W, b in layers)
    return b"S\x00\x00\x00" + struct.pack("<5I", n_in, *shape) + body, n_in, shape


def pth_to_shp(pth_path, out_path=None):
    out_path = out_path or pth_path.rsplit(".", 1)[0] + ".shp"
    pkt, n_in, shape = to_packet(read_layers(pth_path))
    with open(out_path, "wb") as f:
        f.write(pkt)
    return out_path, n_in, shape, len(pkt)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    out, n_in, shape, size = pth_to_shp(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(f"{out}: {n_in}-{'-'.join(map(str, shape))}, {size} bytes")
