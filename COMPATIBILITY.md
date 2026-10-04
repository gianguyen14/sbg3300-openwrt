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

## OpenWrt generation and release support

The audited upstream checkout is `main` at commit
`5edcc1c43cb97048b506168fbbe00538956796d6` (2026-10-04), with kernel 6.18.
The 25.12 stable branch/release is a distinct baseline (kernel 6.12); OpenWrt
25.12 uses APK, while 24.10 uses opkg. The project currently targets the pinned
`main` checkout and must not describe that snapshot as the 25.12.5 release.

Official download indexes checked directly on 2026-10-04 show
`bmips/bcm63268` images in both 24.10.5 and 25.12.5. The OpenWrt BCM63xx
reference page says the old `bcm63xx` target was dropped; this is distinct
from the BCM63xx-family devices carried under the `bmips` target. Its stated
DSL support gap remains relevant: a bmips image for a sibling router does not
provide a working SBG3300 DSL stack. There is no SBG3300 profile in either
release, and the SBG3300 board port remains unvalidated.

Images for sibling boards are reference data only and are not candidates for
this router.

Sources checked:

- https://downloads.openwrt.org/releases/24.10.5/targets/bmips/bcm63268/
- https://downloads.openwrt.org/releases/25.12.5/targets/bmips/bcm63268/
- https://openwrt.org/releases/25.12/start
- https://github.com/openwrt/openwrt/tree/5edcc1c43cb97048b506168fbbe00538956796d6/target/linux/bmips
- https://github.com/openwrt/openwrt/blob/openwrt-24.10/target/linux/bmips/Makefile
- https://github.com/openwrt/openwrt/blob/openwrt-25.12/target/linux/bmips/Makefile
- https://openwrt.org/docs/techref/hardware/soc/soc.broadcom.bcm63xx
