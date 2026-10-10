## Canonical OpenWrt and XTM status

## Current non-DSL milestone

Current priority is Ethernet WAN/LAN and switch feasibility, followed by Wi-Fi,
NAND/boot preparation, USB and peripherals. **DSL is deferred and is not part
of this milestone.** Existing XTM/PTM code, tests, reports and build artifacts
are preserved; its hardware remains inactive. No SAR/FAP, DSL PHY, adsldd,
bcmxtmcfg or XTM platform integration work is being advanced here.

The latest reviewed integration commit is `ee212d7a8920cd7b264693dbc02c86e8a483f7c0`.
The separate working branch for this milestone is
`feat/sbg3300-nondsl-ethernet-wifi`. New read-only stock observations and the
current non-DSL completion boundary are recorded in
`reports/NON-DSL-PRIORITY-2026-10-10.md`.

Pinned OpenWrt commit: `5edcc1c43cb97048b506168fbbe00538956796d6`; Linux 6.18.54; target `bmips/bcm63268`. Target compilation exited 0 in the durable build root. The build and `vmlinux` hashes are recorded in `reports/LOCAL-HANDOFF-STATE.yaml`. Build outputs are not committed.

The inherited XTM external probe is diagnostic, uses probe-only compatibility code, and fails modpost with 19 imports (15 packet-DMA, 3 legacy IRQ, 1 platform MAC allocator); see `reports/XTM-UNRESOLVED-CANONICAL-6.18.54.tsv`. That legacy module remains unlinked. The new, original descriptor/ring and Linux DMA component in `drivers/xtm/` builds as `sbg3300_xtm_dma.ko` against the preserved pinned kernel with no probe shims and no missing kernel imports. It is a ring support component without platform/netdev/DSL integration or hardware validation; see `reports/XTM-DMA-RUNTIME-BUILD.md` and `reports/XTM-BCM63168-CONTRACTS.tsv`. The separate stock `adsldd.ko` (82) and `bcmxtmcfg.ko` (31) inventories are unchanged.

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
| DTS | BUILD-PASS / PARTIAL | DTC/full schema validated; unverified switch/MDIO/NAND disabled, SAR fixture disabled | No | No |
| RAM device-tree range | PARTIAL | DTS retains BMIPS discovery behavior rather than asserting an unproven full range | No | Device boot confirms actual usable memory |
| NAND geometry | PARTIAL / DISABLED | Historical capacity/page/erase evidence retained; legacy ECC code and OOB units are not a verified Linux 6.18 tuple | Stock only | No for geometry; yes for OpenWrt runtime |
| NAND physical map | PARTIAL | Live MTD extents plus exact arithmetic; see [NAND-MAP.md](NAND-MAP.md) | Stock only | Yes to validate OpenWrt behavior |
| NAND image writer / bad-block semantics | INVESTIGATING | Broadcom 4.12L.06B family source strongly corroborates dual slots but is not proven identical to Zyxel’s running writer | No | Exact-source evidence first; device later |
| Fixed partitions / UBI / sysupgrade | NOT-APPROVED | Boot-critical map and writer semantics incomplete | No | Yes, after offline proof |
| Factory image / stock wrapper | NOT-CREATED | No exact compatible container or validated handoff | No | Yes, review and later device validation |
| Ethernet MAC driver | PARTIAL | Upstream bmips support exists; stock board evidence shows `bcm_enet`, `eth3`, `eth4` | Stock only | Yes |
| BCM53125 driver | UPSTREAM-AVAILABLE | Public SBG3300 bootlog for board ID `963168MXH_17A` reports external switch ID 53125; pinned `b53_spi` has the compatible. Compile coverage exists; no SBG runtime bind | No | Yes for runtime |
| Switch silicon | PASS | Public bootlog reports BCM53125 and the same board ID as live stock SSH; boot also reports two MDK switch units and maps their port bitmaps to the two exact-family boardparms groups | Stock only | No for identity; yes for Linux runtime |
| Switch topology / WAN-LAN | PARTIAL / DISABLED | Same-board-ID bootlog verifies BCM53125 and VLAN-1 port group; exact-family source selects HSSPI bus 1/CS0, mode 3/781 kHz and SoC port 6 RGMII; boot VLAN plus Linux BCM53125 profile strongly supports external port 8 as cascade/IMP. Owner-assisted stock A/B/A verifies LAN 1↔`eth0`, LAN 2↔`eth1`, and LAN 4↔`eth3`; stock logical indices 4 and 1 conditionally support external ports 4 and 1 for LAN 1 and LAN 4. LAN 2 index, LAN 3/WAN mappings, exact PHY wiring, RGMII timing, tag compatibility and Linux 6.18 runtime remain unresolved | Stock only | Yes |
| USB | PARTIAL | Stock PCI functions `14e4:6300`; EHCI/OHCI observed | Stock only | Yes for OpenWrt USB runtime |
| Wi-Fi identity | PASS | PCI `14e4:435f`, subsystem `14e4:0513`, class `0x028000`; stock proprietary `wl` family | Stock only | No for identity |
| Wi-Fi upstream binding | INVESTIGATING | b43 has a BCM6362/`0x435f` band-classification case, not proof of PCI discovery/binding; calibration location unresolved | No | Yes for radio validation |
| DSL stock ABI inventory | PASS | `adsldd.ko` and `bcmxtmcfg.ko` are MIPS BE, Linux 2.6.30 SMP/preempt; undefined imports counted | Stock only | No |
| XTM source | PARTIAL | Public Broadcom 4.12L.06B source includes `bcmxtmrt`; depends on missing vendor infrastructure | No | No for porting |
| XTM Linux 6.18 compile probe | ATTEMPTED / FAIL | Corrected harness reached real incompatibilities: NBuff/recycle, DMA types, removed legacy include/API | No | No |
| XTM descriptor/DMA ring + PTM frontend | BUILD-PASS / COMPONENT-ONLY | Original `drivers/xtm/` code, host/sanitizer tests; Linux 6.18.54 `.ko`, compiler/modpost exit 0, no missing kernel imports | No | Yes for later DMA/channel runtime validation |
| `adsldd` / `bcmxtmcfg` source | UNRESOLVED | Implementations absent from inspected mirror; absence there does not prove unavailable elsewhere | No | No for source search |
| DSL sync / XTM board attachment / OpenWrt PPPoE | NOT-TESTED | PTM frontend compiled; controller/DSL attachment and runtime remain blocked | No | Yes |
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

1. Resolve the remaining `963168MXH_17A` switch CPU-port, HSSPI CS, RGMII,
   VLAN, and physical WAN/LAN mappings; leave unsupported nodes disabled.
2. Find and compare the exact Zyxel/Broadcom image-writer lineage with the
   live physical MTD evidence before defining partitions or images.
3. Continue Wi-Fi host/calibration, USB, and peripheral integration work with
   board-specific evidence only.
4. Add offline tests and refine build/reproduction scripts. Preserve XTM/PTM
   sources and artifacts while DSL remains deferred.

Tasks requiring the actual device remain explicitly `NEEDS-DEVICE` in
[HANDOFF-HERMES.md](HANDOFF-HERMES.md). Do not upgrade any status from build
evidence alone.

## PTM frontend milestone

Original IRQ/NAPI/netdev PTM code now builds with the real DMA ring, no probe
shims. Two fresh builds reproduce the same module bytes, all 65 kernel imports
exist. See [reports/XTM-PTM-FRONTEND-BUILD.md](reports/XTM-PTM-FRONTEND-BUILD.md).
Global SAR/FAP ownership, clock/reset/PHY sequencing and DSL events remain
unresolved; no platform binding or physical functionality is claimed.

## Pre-final integration milestone

Real enetsw C resource/lifetime corrections and shared IRQ/channel policy now
compile/link on Linux 6.18.54. Full selected package compilation exits 0, and
three policy tests pass natively, with sanitizers, and under MIPS user-mode QEMU.
Expanded/independent kernels and all implemented modules have genuine results;
see [reports/PRE-FINAL-ENGINEERING.md](reports/PRE-FINAL-ENGINEERING.md) and the
artifact TSVs. Source publication approval is separate from the unresolved
SAR/DSL/topology/calibration/NAND/boot gates. Overall remains PARTIAL-PORT.

## Authorized stock SSH observation, 2026-10-10

Read-only stock SSH succeeded with strict saved-host-key verification. FAP
PacketDMA/XTM ownership, SPI `spi1.0` stock binding, PCI Wi-Fi/USB bindings and
NAND page/OOB/erase metadata corroborated. DSL status Idle; no OpenWrt runtime
test or device modification. External Wi-Fi SROM/calibration provisioning and
SAR/FAP ownership remain blockers. See
[reports/LIVE-READONLY-2026-10-10.md](reports/LIVE-READONLY-2026-10-10.md).

Actual PTM TX callback now checks queue admission before skb mutation. Eight
callback/API-double cases pass native/sanitizer/MIPS tests and catch the old
bug. Two fresh strict external builds reproduce SHA256
`f67b6da34dcc279ee832fbc4210463b8cc89ba2b184186309d324e70e47f80dd`;
OpenWrt component APK rebuilt. Legacy probe still 19 unresolved imports.

Ethernet topology research now cross-checks the exact boardparms C3 branch,
same-board-ID stock bootlog, stock logical-port observations, and Linux 6.18.54
B53/DSA sources. The SBG-specific switch fixture remains disabled; its CS0
contract passes DTC and full schemas. Twenty-two native tests pass. See
[reports/ETHERNET-SWITCH-TOPOLOGY-RESEARCH.md](reports/ETHERNET-SWITCH-TOPOLOGY-RESEARCH.md).
External port 8 is strongly supported as the SoC port-6 cascade endpoint.
Owner-assisted stock A/B/A verifies LAN 1↔`eth0`, LAN 2↔`eth1`, and LAN 4↔
`eth3`. Stock logical indices 4 and 1 conditionally support LAN 1→external
port 4 and LAN 4→external port 1; neither decode proves PCB PHY wiring or
running-binary equivalence. LAN 2's switch index, LAN 3/WAN mapping, exact PHY
wiring, RGMII timing, type-2 tag compatibility and Linux 6.18 runtime remain
unresolved. No new Ethernet kernel module was compiled in this milestone.

Wi-Fi source cross-check identifies a synthetic on-chip PCI presentation in
the exact-family source. BCMA SoC host compiles in isolated coverage; two fresh
BCMA builds reproduce full bytes, but its calibration path remains unresolved
and no board BCMA node is enabled. Additional kernel artifacts audited (77
modules). Initial wrapper failure 127 and lost initial compiler log are explicit
in the report; stable repeat exit 0 is recorded separately. Python tests: 19.
Standalone DTS now matches the conservative patched board; stale-source guard
rejects the old version. Full DTC/schema checks pass with unchanged fixture DTB.

Ethernet RX/NAPI corrections now reject malformed/error descriptors, honor
TX-only zero-budget polling and NAPI completion, and preserve TX status before
reuse. Actual extracted callbacks pass native/ASan/UBSan/MIPS tests. Two strict
module builds reproduce SHA256
`091acf5f6c90fc6f2bebe202343fc295817a4a95b93795e1562efafa396da7d0`, with 85
imports and none missing. Ten OpenWrt patches apply to a fresh pinned tree.
See [reports/ETHERNET-RX-NAPI-VALIDATION.md](reports/ETHERNET-RX-NAPI-VALIDATION.md).
No board activation or OpenWrt runtime result is claimed.
