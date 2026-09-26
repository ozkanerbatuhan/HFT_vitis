# Runbook 3 — Çalışma anında şekil değişimi (kart)

**Amaç:** dört ağı **gerçek şekilleriyle** aynı bitstream'e yüklemek ve her birini
bit-exact doğrulamak. Eski koşumda 40-64-64-32-3 ağı 64-32-16-3'e kırpılmıştı ve
genişlik register'ları hiç yazılmamıştı (bkz. commit `4730872`).

**Gerekmeyen:** RTL değişikliği, sentez, yeni bitstream.
**Gereken:** firmware'i derleyip BOOT.bin yenilemek + 4 koşum.

Kartsız yapılanlar (tamam):
- RTL simülasyonu `mlp_shape_tb`: 4 ağ arka arkaya, reset yok → 1000/1000 bit-exact,
  çevrim sayacı her ağda denkleme uyuyor.
- Firmware yükleyicisi PC'de derlenip `.shp` ile beslendi → AXI yazma dizisi
  simülasyondakiyle birebir aynı.

---

## Adım 1 — Firmware

Vitis → `lwip_echo_server` → **Build**. Sonra BOOT.bin (mevcut bitstream ile):

```
cd D:\vitis_projects\lwip_echo_server
bootgen -image ..\verify_boot.bif -arch zynq -o BOOT.bin -w on
```

Boyut ~4,8 MB olmalı. SD karta kopyala, kartı aç.

## Adım 2 — Engine

Linux engine yeniden derlenmeli (`.shp` desteği eklendi):

```bash
cd /mnt/d/vitis_projects/pc_test/linux
g++ -O2 -o hft_engine_linux hft_engine_linux.cpp -lpthread
```

> Bu Windows makinesinde şu an Ubuntu WSL yok (yalnız `docker-desktop`).
> Engine'i nerede koşturduysan orada derle.

## Adım 3 — Dört koşum

GUI artık `.pth` seçildiğinde modeli **şekilli** (`.shp`) gönderiyor. Log'da
`Shaped model 40-64-64-32-3 (35876 bytes)` satırını gör; UART'ta
`Shaped model loaded: 40-64-64-32-3`.

Kartı **resetlemeden** dördünü arka arkaya koş:

```bash
HFT_LOG=log_shape_64_32_16.csv  ./hft_engine_linux    # mlp_40_64_32_16_3
HFT_LOG=log_shape_64_64_32.csv  ./hft_engine_linux    # mlp_40_64_64_32_3
HFT_LOG=log_shape_32_16_8.csv   ./hft_engine_linux    # mlp_40_32_16_8_3
HFT_LOG=log_shape_10_16_8.csv   ./hft_engine_linux    # mlp_40_10_16_8_3
```

GUI: Select Model → `verify/models/<ilgili>.pth` → Send Model → Select CSV →
`verify/verify_stream.csv` → delay 0 → Start Stream.

## Adım 4 — Doğrula

```bash
cd /mnt/d/vitis_projects/pc_test/verify
python3 verify_bitexact.py --real-shape --stream verify_stream.csv \
    --log ../linux/log_shape_64_64_32.csv --model models/mlp_40_64_64_32_3_7e3943ab.pth
```

(dördü için tekrarla). Beklenen: `RESULT: BIT-EXACT VERIFIED`.

**Çevrim sayacı** (`cycles` sütunu) ağa göre değişmeli — makalenin
denklemi (1) eksi bir:

| Ağ | Denklem (1) | `cycles` sütunu |
|---|---:|---:|
| 40-64-32-16-3 | 96 | 95 |
| 40-64-64-32-3 | 112 | 111 |
| 40-32-16-8-3 | 77 | 76 |
| 40-10-16-8-3 | 70 | 69 |

Logları bana ver; makaledeki doğrulama tablosunu ve Bölüm 5.10'u bunlarla
yeniden yazacağım.
