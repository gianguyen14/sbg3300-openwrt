# Port status

Status vocabulary: `PASS` means direct evidence for that layer only;
`INVESTIGATING` means active research; `UNKNOWN` means no adequate evidence;
`NOT-TESTED` means no runtime claim.

| Area | Status | Evidence / limitation |
|---|---|---|
| CPU / SoC | PASS (stock observation) | `/proc/cpuinfo`: 963168MXH_17A, dual Broadcom4350 V8.0; dmesg chipId 0x631680D0 |
| OpenWrt bmips target | PASS (source exists) | Current official checkout has `bcm63268`; kernel patch baseline 6.18 |
| Upstream reference devices | PASS | Actiontec T1200H; Sagemcom F@ST 3864 OP; other BCM63168 devices |
| RAM | PASS (stock observation) | `/proc/meminfo` reports 123392 KiB; vendor boot log says BPM total 128 MiB |
| NAND geometry | PASS (controller observation) | 128 MiB, page 2048, OOB 64, ECC step 512/strength 15, BBT enabled |
| Physical NAND map | PARTIAL | Live dmesg gives MTD physical extents; 4.12L.06B source model explains 128 KiB boot block, dual rootfs, 4 MiB data and 1 MiB BBT, but exact 2018 active-rootfs and bad-block map remain unresolved |
| Board parameters | PASS (matching source entry) | Public BCM63168D0 source has exact `963168MXH_17A` table; source-to-running-build equivalence remains |
| SBG3300 DTS | INVESTIGATING | Research skeleton enables observed USB, PCIe and NAND controller/ECC only; no partitions, Ethernet/DSA, GPIOs or MAC offsets until verified |
| Ethernet MAC / ports | INVESTIGATING | Board table shows two MAC/switch groups and SPI SSB0 external switch; physical LAN labels/CPU port unresolved |
| BCM53125 | LIKELY, not proven | External SPI switch path is confirmed by board table; exact live switch ID is not yet read |
| USB | PASS (controller observation) | PCI 14e4:6300 OHCI and EHCI both enumerate |
| Wi-Fi | INVESTIGATING | PCI 14e4:435f, stock `wl` driver reports BCM435f; calibration/driver path unresolved |
| DSL/XTM | INVESTIGATING | Stock modules are ELF32 MSB MIPS32, vermagic Linux 2.6.30 SMP/preempt; 4.12L.06B source has `bcmxtmrt`; `adsldd`/`bcmxtmcfg` implementation absent from mirror; modern port not built |
| Hardware acceleration | INVESTIGATING | FAP/BPM modules are active in stock; no upstream equivalent established |
| Firmware container | UNKNOWN | stock updater image and physical NAND target are not fully mapped for OpenWrt payloads |
| Recovery / no UART | UNKNOWN | no exact static proof of recovery path yet |
| Build | INVESTIGATING | official bmips baseline selected; unmodified build is compiling host/tool dependencies (slow GNU mirror downloads); no target artifact yet |
| Flash | PROHIBITED | not authorized in this phase; all artifacts remain offline-only |

Overall: `RESEARCHING`.
