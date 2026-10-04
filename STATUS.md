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
| SBG3300 DTS | BUILD-PASS / NOT-RUNTIME-TESTED | Full pinned upstream profile build succeeds; resulting DTB has SBG3300 compatible, no serial console, and only observed controller nodes. Ethernet/DSA, fixed partitions, GPIOs, and MAC offsets remain absent/unresolved |
| SBG3300 profile config | BUILD-PASS / OFFLINE-ONLY | `CONFIG_TARGET_bmips_bcm63268_DEVICE_zyxel_sbg3300-n000` resolves and profile produced an initramfs loader ELF; no stock CFE compatibility is established |
| Ethernet MAC / ports | INVESTIGATING | Board table shows two MAC/switch groups and SPI SSB0 external switch; physical LAN labels/CPU port unresolved |
| BCM53125 | LIKELY, not proven | External SPI switch path is confirmed by board table; exact live switch ID is not yet read |
| USB | PASS (controller observation) | PCI 14e4:6300 OHCI and EHCI both enumerate |
| Wi-Fi | UNSUPPORTED for initial bring-up | Exact live ID is 14e4:435f/BCM435F pseudo-device; no matching upstream PCI driver; close BCM63168-family reference also reports no usable driver; no open `wl` source found in 4.12L.06B tree |
| DSL/XTM | SOURCE-INCOMPLETE / PORT PROBE FAILED | Stock ADSL/config modules have 2.6.30 vermagic and 82/31 undefined imports; available XTM C source hits NBuff recycle, DMA type/config, and removed `asm/system.h` mismatches against 6.18; `adsldd`/`bcmxtmcfg` implementations absent from inspected mirror |
| Hardware acceleration | INVESTIGATING | FAP/BPM modules are active in stock; no upstream equivalent established |
| Firmware container | UNKNOWN | stock updater image and physical NAND target are not fully mapped for OpenWrt payloads |
| Recovery / no UART | UNKNOWN | no exact static proof of recovery path yet |
| Build | BASELINE-PASS / SBG3300-INITRAMFS-PASS | unmodified bmips baseline and SBG3300 research profile full builds exit 0; candidate is only an offline initramfs loader ELF, not a stock image (`reports/SBG3300-OFFLINE-INITRAMFS.md`) |
| Flash | PROHIBITED | not authorized in this phase; all artifacts remain offline-only |

Overall: `PARTIAL-PORT`. No device boot or runtime hardware validation is claimed.
