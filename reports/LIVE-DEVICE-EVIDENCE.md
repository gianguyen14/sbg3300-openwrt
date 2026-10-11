# SBG3300-N000 Live Device Hardware Evidence

Collected securely via read-only SSH wrapper on stock firmware.

## Hardware Truths (Stock Kernel 2.6.30)
- **SoC:** BCM63168 (`963168MXH_17A`), BMIPS4350 CPU.
- **Wi-Fi:** PCI `0000:00:00.0` ID `14e4:435f`, proprietary `wl` driver.
- **Ethernet:** `bcmsw`, `eth0`-`eth3` (LAN), `eth4` (WAN), `eth5`.
- **SPI/NAND:** `bcmhs_spi.1`, `bcmleg_spi.0`, `brcmnand.0`, `spi1.0`.
- **USB:** EHCI (`14e4:6300` / `1d6b:0002`), OHCI (`1d6b:0001`).
- **DSL:** `adsldd`, IRQ 31 (Not supported in OpenWrt, ignored).

## Blockers Resolved for DTS Mapping
1. SoC and target identify definitively as `bcm63168`.
2. Wireless ID confirms BCM435f (`14e4:435f`). Upstream compatibility (b43/brcmsmac/brcmfmac) needs explicit verification.
3. Switch topology matches standard 6-port BCM63xx layout (eth0-5).
4. Storage is confirmed standard Broadcom NAND (`brcmnand`).
## Switch and NAND Evidence Addendum (Phase 2, Stock 2.6.30)
- **NAND Flash Layout (`/proc/mtd`)**: `erasesize` is `0x20000` (128 KiB).
  - `mtd0` (rootfs): `0x016a0000` (~22.625 MiB).
  - `mtd1` (data): `0x00400000` (4.0 MiB).
  - `mtd2` (nvram): `0x00020000` (128 KiB).
- **Network Interface Map**:
  - `eth0` - `eth3`: 4 LAN ports (shared base MAC). Test showed Gigabit capability on link up.
  - `eth4`: Dedicated WAN port (unique MAC). Test showed Gigabit capability on link up.
  - `eth5`: Internal CPU link (No MII transceiver).
  - Switch is configured through UBUS (`ethswctl` reports ID 0x63168, Port Map 0x58, Phy Map 0x18).
- **GPIO / LEDs**: Sysfs is disabled in stock 2.6.30. Pin definitions must be generated from GPL boardparams for `963168MXH_17A`.
