## Canonical OpenWrt and XTM status

Pinned OpenWrt commit: `5edcc1c43cb97048b506168fbbe00538956796d6`; Linux 6.18.54; target `bmips/bcm63268`. Target compilation exited 0 in the durable build root. The build and `vmlinux` hashes are recorded in `reports/LOCAL-HANDOFF-STATE.yaml`. Build outputs are not committed.

The XTM external build is diagnostic, uses probe-only compatibility code, and fails modpost. Object scan found 19 unique symbols absent from the linked objects and pinned kernel exports; see `reports/XTM-UNRESOLVED-CANONICAL-6.18.54.tsv`. No XTM `.ko` exists; no runtime claim is made.

**Overall: `PARTIAL-PORT` · `OFFLINE-ONLY` · `NOT-FLASHABLE`.** No OpenWrt
image has been booted on the SBG3300. No flash/factory/sysupgrade image exists.

Evidence vocabulary is defined in [docs/EVIDENCE-POLICY.md](docs/EVIDENCE-POLICY.md).
`PASS` applies only to the stated layer. In particular, a successful build is
not runtime evidence.

| Component | Status | Evidence | Runtime tested on SBG3300? | Needs device? |
|---|---|---|---|---|
| Device identity | PASS | LIVE-DEVICE reports identify Zyxel SBG3300-N000 | Yes, stock only | No |
| Board | PASS | `963168MXH_17A` observed live and exact boardparms entry found in FAMILY-SOURCE | Yes, stock only | No |
| SoC | PASS | BCM63168D0, chip ID `0x631680D0` in stock boot evidence | Yes, stock only | No |
| CPU | PASS | BMIPS4350-class, two cores, MIPS32 big-endian/o32; stock reports | Yes, stock only | No |
| RAM | PASS | 128 MiB physical evidence; stock `MemTotal` about 123392 KiB | Yes, stock only | No |
| Upstream OpenWrt baseline | PASS | Official `openwrt/openwrt`, commit `5edcc1c43cb97048b506168fbbe00538956796d6`; unmodified bmips build exited 0 | No OpenWrt runtime | No |
| Kernel baseline | PASS | Build report records Linux 6.18.54 | No | No |
| SBG3300 profile | BUILD-PASS | Profile selected and dedicated build exited 0; patch series under `patches/openwrt/` | No | No |
| SBG3300 initramfs ELF | OFFLINE-ONLY | 5,925,020 bytes; SHA256 `3961a39d5d554ce467b9575bbc6f6293d385ddda9fc4dc9b3dbf0c3cf8027b51`; local artifact only | No | No |
| DTS | BUILD-PASS / PARTIAL | DTC build and round-trip recorded; intentionally incomplete and conservative | No | No |
| RAM device-tree range | PARTIAL | DTS retains BMIPS discovery behavior rather than asserting an unproven full range | No | Device boot confirms actual usable memory |
| NAND geometry | PASS | Live stock controller evidence: 128 MiB, 2 KiB page, 64 B OOB, 128 KiB eraseblock, 512-byte ECC step, strength 15, on-flash BBT | Stock only | No for geometry; yes for OpenWrt runtime |
| NAND physical map | PARTIAL | Live MTD extents plus exact arithmetic; see [NAND-MAP.md](NAND-MAP.md) | Stock only | Yes to validate OpenWrt behavior |
| NAND image writer / bad-block semantics | INVESTIGATING | Broadcom 4.12L.06B family source strongly corroborates dual slots but is not proven identical to Zyxel’s running writer | No | Exact-source evidence first; device later |
| Fixed partitions / UBI / sysupgrade | NOT-APPROVED | Boot-critical map and writer semantics incomplete | No | Yes, after offline proof |
| Factory image / stock wrapper | NOT-CREATED | No exact compatible container or validated handoff | No | Yes, review and later device validation |
| Ethernet MAC driver | PARTIAL | Upstream bmips support exists; stock board evidence shows `bcm_enet`, `eth3`, `eth4` | Stock only | Yes |
| BCM53125 driver | UPSTREAM-AVAILABLE | Upstream `b53_spi` has `brcm,bcm53125`; similar board use is only a reference | No | No for source research; yes for silicon/topology/runtime |
| Switch silicon/topology | UNPROVEN | HS-SPI path and boardparms groups are known; exact switch ID, CPU port, timings, and jack mapping are not | No | Yes |
| USB | PARTIAL | Stock PCI functions `14e4:6300`; EHCI/OHCI observed | Stock only | Yes for OpenWrt USB runtime |
| Wi-Fi identity | PASS | PCI `14e4:435f`, subsystem `14e4:0513`, class `0x028000`; stock proprietary `wl` family | Stock only | No for identity |
| Wi-Fi upstream binding | INVESTIGATING | b43 has a BCM6362/`0x435f` band-classification case, not proof of PCI discovery/binding; calibration location unresolved | No | Yes for radio validation |
| DSL stock ABI inventory | PASS | `adsldd.ko` and `bcmxtmcfg.ko` are MIPS BE, Linux 2.6.30 SMP/preempt; undefined imports counted | Stock only | No |
| XTM source | PARTIAL | Public Broadcom 4.12L.06B source includes `bcmxtmrt`; depends on missing vendor infrastructure | No | No for porting |
| XTM Linux 6.18 compile probe | ATTEMPTED / FAIL | Corrected harness reached real incompatibilities: NBuff/recycle, DMA types, removed legacy include/API | No | No |
| `adsldd` / `bcmxtmcfg` source | UNRESOLVED | Implementations absent from inspected mirror; absence there does not prove unavailable elsewhere | No | No for source search |
| DSL sync / XTM netdev / OpenWrt PPPoE | NOT-TESTED | Compile work is not line synchronization or data-path evidence | No | Yes |
| FAP/HNAT | DEFERRED | Vendor FAP/BPM/ingress-QoS observed in stock; portability unknown | No | No for initial software-routing bring-up |
| Recovery route | UNPROVEN | No exact non-console route proven for this model/revision | No | Yes |
| Runtime boot / LAN / DSA / Wi-Fi / DSL / PPP | NOT-TESTED | No OpenWrt runtime tests have occurred | No | Yes |
| Flash | PROHIBITED | User explicitly requires offline safety gates and no flash in this task | No | Explicit future authorization plus all gates |

## Exact image/build facts

- OpenWrt remote: `https://github.com/openwrt/openwrt.git`.
- Pinned upstream commit: `5edcc1c43cb97048b506168fbbe00538956796d6` (`main` at
  research time; pin the commit, not a moving branch).
- The SBG3300 patch series applies on that base. Its resulting local port head
  at research time was `18c17336871e73ddfbab3198104d8c42df844146`.
- Target: `bmips/bcm63268`; recorded kernel: Linux `6.18.54`.
- SBG3300 output is an initramfs loader ELF, **not** a Broadcom/Zyxel factory
  container, CFE-tested ELF, sysupgrade image, or runtime-tested firmware.
- The exact current local artifact SHA256 is recorded above and in
  `reports/SBG3300-OFFLINE-INITRAMFS.md`; generated artifacts are not committed.

## Next offline work

1. Continue the XTM port as small compile-probe patches; do not wholesale
   transplant old Linux headers or vendor-modified networking internals.
2. Reconstruct exact `963168MXH_17A` Ethernet topology from source and safely
   available board evidence; leave unsupported nodes disabled.
3. Find and compare the exact Zyxel/Broadcom image-writer lineage with the
   live physical MTD evidence before defining partitions or images.
4. Continue public source searches for `adsldd`/`bcmxtmcfg` and Wi-Fi bus glue.
5. Add offline tests and refine build/reproduction scripts.

Tasks requiring the actual device remain explicitly `NEEDS-DEVICE` in
[HANDOFF-HERMES.md](HANDOFF-HERMES.md). Do not upgrade any status from build
evidence alone.
