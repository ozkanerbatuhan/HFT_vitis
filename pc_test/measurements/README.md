# Measurement logs

Raw per-request logs behind the latency results of the paper, gzip-compressed.
All runs use the same board, bitstream and models; each file has one row per
request.

| File | Host | Network | Requests | Used in |
|---|---|---|---|---|
| `linux_native_10_16_8.csv.gz` | native Linux | 40-10-16-8-3 | 100,000 | Table 4, Table 6 |
| `linux_native_32_16_8.csv.gz` | native Linux | 40-32-16-8-3 | 100,000 | Table 4, Table 6 |
| `linux_native_64_32_16.csv.gz` | native Linux | 40-64-32-16-3 | 100,000 | Table 4, Table 6, Fig. 4 |
| `linux_native_64_64_32.csv.gz` | native Linux | 40-64-64-32-3 | 100,000 | Table 4, Table 6 |
| `windows_*.csv.gz` | Windows | as above | 100,000 each | Section 5.2, Fig. 4 |
| `linux_jitter_64_32_16.csv.gz` | Linux | 40-64-32-16-3 | 100,000 | Section 5.5 (cycle count) |

The per-stage breakdown of Table 8 comes from
`../_archive_pre_verify/2026-07-12_1M-paket_TABLO10-KAYNAGI.csv.gz`
(1,004,229 packets).

## Columns

Linux logs:

- `Timestamp_us` – host send time
- `Latency_us` – host round trip, send to reply
- `Result` – decision returned by the board
- `recv_ticks`, `parse_ticks`, `dma_ticks`, `pl_ticks`, `read_ticks` – on-board
  stage durations in Zynq Global Timer ticks (333.33 MHz, 3 ns)
- `out0`..`out2` – the three raw 16-bit Q8.8 outputs of the core, compared
  against the golden model by `../verify/verify_bitexact.py`
- `cycles` – core cycle counter, start to done (see the paper, Section 5.5)

Windows logs carry only `Timestamp_us`, `Latency_us` and `Result`.
