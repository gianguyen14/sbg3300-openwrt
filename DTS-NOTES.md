# DTS notes

## Current upstream base

`target/linux/bmips/dts/bcm63268.dtsi` already describes BCM63168-class BMIPS4350
CPUs, clocks, interrupts, GPIO/pinctrl, NAND controller, Ethernet/switch
controller, PCIe, and USB controller nodes. `target/linux/bmips/bcm63268` uses
Linux 6.18 in the pinned upstream checkout.

## SBG3300 evidence-supported draft

The research-only DTS draft is kept in `dts/bcm63168-zyxel-sbg3300-n000.dts`.
It intentionally avoids unproven board GPIOs, fixed NAND partitions, MAC
offsets, and switch port labels. `bcm63268.dtsi` defines `memory@0` with
`reg = <0 0>`, which leaves RAM discovery to BMIPS rather than claiming a
board-fixed base/size. The live device reports 128 MiB physical RAM and Linux
reports 123392 KiB; no vendor-reserved range has been established. The draft
enables the SoC NAND controller with the directly observed 512-byte ECC
step, strength 15, 64-byte OOB sector, and on-flash BBT, but defines no
partitions. It also clears inherited `earlycon`/`stdout-path`, so the board DTS
does not select or depend on a UART console. This is suitable for offline
DTB/initramfs build review only; it does not make a firmware image, bootloader
handoff, or writable flash layout safe.

The exact `963168MXH_17A` table was found in the public BCM963xx 4.12L.06B
source candidate at
`source/vendor/bcm963xx_4.12L.06B_consumer/shared/opensource/boardparms/bcm963xx/boardparms.c`.
It defines two Ethernet switch groups: one memory-mapped group (`portMap 0x58`,
PHY 3/4 direct connections and port 6 RGMII external-switch connection) and a
second group on HS-SPI SSB0 (`portMap 0x1e`, PHY IDs 1–4). This is evidence for
an external HS-SPI switch connection, but does not prove the actual switch
silicon is BCM53125 or map user-visible LAN jacks to DSA ports. The same source
sets AFE IDs for internal 6302 Annex A and external 6306/6302 line-driver paths.
These are board-parameter facts, not yet verified live AFE selection.

The table supplies LED assignments and active levels (including LEDs on
serial GPIO expanders), plus reset and SES external-interrupt indices. Those
values remain documentation-only: the reset event polarity/debounce and board
electrical behavior are not fully reconstructed, so no reset-key handler is
enabled in the DTS. The initial skeleton does not enable Ethernet and must not
be treated as a bootable device definition.

## Remaining proof

- exact board-compatible chain / board ID relationship and equivalence of the
  source table to the 2018 running build;
- NAND ECC/OOB layout and physical partition map;
- internal Ethernet port/MDIO mapping and external switch attachment;
- WLAN PCIe function/calibration source;
- LEDs/buttons GPIO and active polarity;
- AFE/DSL board parameters.
