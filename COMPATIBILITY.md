# Compatibility matrix

| Feature | OpenWrt support in family | SBG3300 evidence | Status |
|---|---|---|---|
| BMIPS4350 / BCM63168 | bmips `bcm63268` target and sibling DTS exist | exact SoC/chip ID observed | upstream substrate present; board unvalidated |
| 128 MiB RAM | bcm63268 runtime autodetection exists | 128 MiB observed | likely supported; boot not tested |
| NAND | brcm NAND driver and NAND images exist | 128 MiB, 2K/64 OOB, ECC 15/512 observed | layout/ECC match needs proof |
| Ethernet | BCM63xx Ethernet drivers available | vendor `bcm_enet`, eth3/eth4 | topology/ports unresolved |
| BCM53125 | b53 DSA driver and reference DTS | not directly identified on SBG3300 | unknown |
| USB | EHCI/OHCI nodes and packages exist | both controllers observed | likely, not OpenWrt runtime-tested |
| Wi-Fi | Broadcom driver choices vary | PCI 14e4:435f, proprietary `wl` | unknown/experimental |
| DSL/XTM | no demonstrated current-kernel port for this board | proprietary 2.6.30 stack observed | active investigation |
| FAP/BPM acceleration | vendor modules only identified | active in stock | vendor-only / unknown portability |
| Web-updater factory image | family-specific CFE formats exist | exact Zyxel writer/layout incomplete | prohibited / unsupported |
| sysupgrade | generic image formats exist | partition/bad-block map incomplete | disabled/not implemented |
