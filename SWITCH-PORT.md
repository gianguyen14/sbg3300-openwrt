# Ethernet and switch investigation

The upstream `bmips` target has BCM63168 Ethernet and DSA `b53` support. Its
generic `b53_spi` frontend supports `brcm,bcm53125`, in addition to MDIO/SRAB
frontends. The exact-board board-parameter table found in the Broadcom 4.12L.06B
source configures an external switch on `BP_ENET_CONFIG_HS_SPI_SSB_0`, with PHY
group port map `0x1e` (ports 1 through 4), and a separate memory-mapped group
with port map `0x58` (ports 3, 4, and 6). In the source's selected board-table
branch, the memory-mapped group describes port 4 as `TMII_DIRECT|0x14` and
port 6 as `RGMII_DIRECT|EXTSW_CONNECTED`. This proves an external SPI switch
path and an additional SoC-side Ethernet path in the matching board table, but
not the currently detected silicon ID or how the running 2018 binary applies
those PHY settings. A fresh read-only search of live `dmesg` for switch-ID
messages returned no matching line. Live sysfs does expose
`/sys/devices/platform/bcmhs_spi.1/spi1.0`, bound to the generic
`bcm_HSSpiDev0` driver with `MODALIAS=bcm_HSSpiDev0`; it does not identify a
BCM53125 device or expose the switch register ID.

The upstream tree also contains a BCM53125 DSA configuration for Sagemcom
F@ST 3864 OP. This establishes driver availability, not identical port wiring.

Stock boot evidence shows `bcm_enet`, `eth3` and `eth4`, switch-port indices
1, 11, and 12 in link logs, and WAN layering through `eth4.1` to `eth4`. The
physical LAN port labels, MAC connection, detected external switch ID, RGMII
timing, DSA CPU port, and relationship between SPI-managed external switch and
internal switch ports remain unresolved. Do not cargo-cult reference DTS
labels.
