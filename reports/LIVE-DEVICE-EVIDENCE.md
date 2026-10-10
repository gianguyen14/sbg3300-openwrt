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
