# Hermes Remote Handoff

## Startup — copy/paste

```sh
git clone https://github.com/gianguyen14/sbg3300-openwrt.git
cd sbg3300-openwrt
cat AGENTS.md
cat STATUS.md
cat HANDOFF-HERMES.md
cat REPRODUCE.md
```

Hermes has no physical SBG3300, router SSH, modem, or LAN access. Do not ask
for router access unless the selected task is explicitly `NEEDS-DEVICE`.
Continue offline work automatically. **Never flash, factory-reset, use UART, or
perform raw MTD/NAND operations.**

## 1. Project objective

Port full upstream OpenWrt to the Zyxel SBG3300-N000 while preserving its
Broadcom BCM63168 hardware support: NAND, Ethernet/switch, USB, Wi-Fi if
feasible, DSL/XTM/PPPoE if feasible, and a safe stock-compatible upgrade and
recovery path. The currently working stock-custom router is separate and must
not be disturbed. This repository is the port research, not a replacement for
that system.

## 2. Absolute safety constraints

- Current state is `PARTIAL-PORT`, `OFFLINE-ONLY`, `NOT-FLASHABLE`.
- No generated SBG3300 image is approved for installation. No candidate has
  booted on hardware.
- No UART or serial-console dependency. Do not propose or request UART access.
- No router changes, reboot, firmware upload/flash, factory reset, raw MTD,
  CFE, bootloader, NVRAM, PPP credentials, MAC, or calibration changes.
- Keep stock firmware and all local device-specific/proprietary material out
  of Git and GitHub.
- Keep unknown DTS nodes/partitions disabled. A similar board is not proof.

## 3. What has already been proven

Evidence labels are defined in `docs/EVIDENCE-POLICY.md`; consult
`STATUS.md` for the authoritative matrix.

- `LIVE-DEVICE`/`STOCK-BOOT-LOG`: model SBG3300-N000, board `963168MXH_17A`,
  BCM63168D0 chip ID `0x631680D0`, 128 MiB RAM/NAND, MIPS big-endian, and stock
  Linux 2.6.30. Stock `MemTotal` is around 123392 KiB.
- `LIVE-DEVICE`: NAND reports 2 KiB page, 64-byte OOB, 128 KiB eraseblocks.
  Historical ECC value 15 is not an established Linux 6.18 strength/step
  tuple; current stock sysfs lacks those attributes. On-flash BBT and the
  physical Linux MTD extents are
  documented in `NAND-MAP.md`.
- `EXACT-BOARD-SOURCE`: public Broadcom family source has an entry for
  `963168MXH_17A`. Its equivalence to the running Zyxel 2018 build is not
  established.
- `BUILD-RESULT`: official OpenWrt bmips/bcm63268 baseline and the SBG3300
  profile build completed successfully at the commit/kernel below.
- `BUILD-RESULT`: SBG3300 DTS compiles and was round-trip checked. Its
  incompleteness is deliberate; it does not assert speculative switch
  topology, GPIOs, partitions, or serial console.
- `STOCK-BINARY`: local-only module metadata identifies stock DSL/XTM modules
  as MIPS BE Linux 2.6.30 modules; raw modules are not published.
- `FAMILY-SOURCE` plus a real compile probe: public `bcmxtmrt` XTM source was
  attempted against OpenWrt Linux 6.18 and fails on actual vendor ABI/API
  dependencies after correcting an initial path-with-spaces harness error.
- `LIVE-DEVICE`: PCI Wi-Fi function is `14e4:435f`, subsystem `14e4:0513`;
  stock driver is proprietary `wl` family `6.30.102.7.cpe4.12L06B.1`.
- `UPSTREAM`: b53 SPI supports `brcm,bcm53125`; a similar BCM63168 device uses
  it. Neither fact proves the SBG3300's switch silicon/topology.

## 4. What has NOT been proven

- OpenWrt boot, CFE handoff, or usable board RAM under OpenWrt.
- Ethernet link, exact MAC selection, switch silicon ID, DSA CPU port, RGMII
  timing, or mapping from LAN jacks to ports.
- NAND OpenWrt read/write, ECC/OOB compatibility, complete writer semantics,
  safe partition scheme, bad-block translation, or image acceptance.
- DSL driver port, DSL initialization, sync, XTM interface, PPPoE, or Internet.
- OpenWrt Wi-Fi PCI discovery/binding, calibration, association, or regulatory
  behavior.
- USB runtime, acceleration/HNAT, safe no-UART recovery, stock web image
  acceptance, factory image, or sysupgrade.

Do not change these to PASS based on compilation, static matching, or sibling
hardware.

## 5. Exact OpenWrt baseline commit

- Repository: `https://github.com/openwrt/openwrt.git`
- Pinned commit: `5edcc1c43cb97048b506168fbbe00538956796d6`
- Branch at research capture: `main` (commit, not branch name, is the pin).
- Target/subtarget: `bmips/bcm63268`.
- Recorded kernel: Linux `6.18.54`.
- Build config generation now uses the current APK package generation in the
  pinned tree (`CONFIG_USE_APK=y`).

## 6. Reproduce baseline build

Use `REPRODUCE.md` and `tools/prepare-openwrt.sh baseline`. The script clones
the pinned upstream revision into a space-free cache path unless
`OPENWRT_DIR` is set, refuses unexpected/dirty source, and does not touch the
router. Then run `tools/build-openwrt.sh baseline`. The build is large and may
take substantial time. A historical completed build produced an ELF32
big-endian MIPS/o32 `vmlinux` with SHA256
`04ca95b76fe03c6a6de3fc86e29ee0d7eb522f4ec2cc21b8700f0e3aaa64ab9b`.
Sibling-device firmware artifacts from that build are not SBG3300 images.

## 7. Reproduce SBG3300 offline initramfs build

Run `tools/prepare-openwrt.sh port`, then `tools/build-sbg3300-profile.sh`.
The script applies the checked-in patch series to the pinned base and validates
the tested port source tree before building. It emits only a research initramfs
loader ELF and related local evidence. Historical exact ELF SHA256:
`3961a39d5d554ce467b9575bbc6f6293d385ddda9fc4dc9b3dbf0c3cf8027b51`.
Rebuild output may vary with feeds/toolchain environment; inspect and record
the exact new hash. Never treat it as a factory image or attempt to load it.

## 8. Patch series order

`patches/openwrt/series` is authoritative:

1. `0001-bmips-add-offline-sbg3300-n000-skeleton.patch`
2. `0002-bmips-label-sbg3300-initramfs-offline-only.patch`
3. `0003-bmips-format-sbg3300-dts-comments.patch`
4. `0004-bmips-sbg3300-no-uart-console.patch`

They apply on the pinned upstream commit. They add a conservative research DTS
and initramfs-only profile. There is no factory or sysupgrade recipe.

## 9. DTS current assumptions

File: `dts/bcm63168-zyxel-sbg3300-n000.dts`; the skeleton is carried in
patch 0001 and subsequent integration patches in `patches/openwrt/series`.
It identifies Zyxel SBG3300-N000/BCM63168 and retains BMIPS memory discovery
behavior. Current integration disables NAND and removes unverified ECC/OOB
overrides; there are no partitions. It disables unresolved Ethernet configuration and does not
assign board GPIOs, switch ports, or MAC offsets. `/chosen` does not require a
serial console. Every node is still runtime-unvalidated.

## 10. NAND state

Total observed capacity is `0x08000000`. Live physical registrations:

| Physical extent | Observation |
|---|---|
| `0x00000000–0x00020000` | `nvram` MTD registration |
| `0x00020000–0x04020000` | unregistered/unknown |
| `0x04020000–0x056c0000` | live `rootfs` extent (`0x016a0000`) |
| `0x056c0000–0x07b00000` | unregistered/unknown |
| `0x07b00000–0x07f00000` | `data` MTD (4 MiB) |
| `0x07f00000–0x08000000` | reserved/unregistered 1 MiB tail |

Broadcom 4.12L.06B family source models two rootfs slots, a 128 KiB boot
block, bad-block-aware addressing, 4 MiB data, and a 1 MiB BBT tail. The
midpoint plus one eraseblock equals the live rootfs start. This is strong
corroboration, not proof that the running 2018 Zyxel image writer is identical.
Fixed partitions, UBI conversion, sysupgrade, and factory image remain
unapproved. See `NAND-MAP.md`.

## 11. Ethernet/switch state

Exact boardparms branch `963168MXH_17A` configures an external HSSPI switch
group (`BP_ENET_CONFIG_HS_SPI_SSB_0`, PHY map `0x1e`) and a separate memory
mapped group (`0x58`). It describes port 4 as `TMII_DIRECT | 0x14` and port 6
as `RGMII_DIRECT | EXTSW_CONNECTED`. Live stock evidence has `bcm_enet`,
`eth3`, `eth4`; WAN is `ppp2.1 -> eth4.1 -> eth4`; boot logs mention switch
indices 1, 11, 12. HSSPI sysfs path is observed.

Unresolved: exact switch silicon ID, CPU port, MAC role, RGMII timing, meanings
of eth3/eth4 and VLAN, external jack mapping, and how SPI indices map to jacks.
Do not enable speculative DSA topology. `b53_spi` driver availability is only
upstream evidence.

## 12. DSL/XTM state

The stock path looks PPPoE-like (`ppp2.1` over `eth4.1`), but precise XTM/PTM/
ATM data flow must be derived from stock source and logs, not guessed from the
interface names. `adsldd.ko` (~402804 bytes) and `bcmxtmcfg.ko` (~99000 bytes)
are local-only MIPS BE Linux 2.6.30 SMP/preempt modules. Undefined imports were
inventoried (82 and 31 unique). Public family source provides `bcmxtmrt`, but
not complete `adsldd` or `bcmxtmcfg` implementations and depends on old
Broadcom blog/NBuff, packet DMA, FAP/BPM/IQoS, board glue, and legacy kernel
extensions.

The Linux 6.18 compile probe did run. First failure due to include path with
spaces was a harness issue; corrected probe reached actual incompatibilities:
NBuff/recycle structures, DMA types, legacy `asm/system.h`, and other vendor
extensions. Keep this history in `reports/DSL-6.18-COMPILE-PROBE.md` and
`reports/DSL-UNRESOLVED-SYMBOLS.md`. DSL port is in progress, not complete;
no module loads or DSL sync have been tested.

## 13. Wi-Fi state

Exact stock PCI identity is `14e4:435f`, subsystem `14e4:0513`, class
`0x028000`; stock uses proprietary `wl` with reported family
`6.30.102.7.cpe4.12L06B.1`. Linux b43 has a `0x435f`/BCM6362 band
classification case, but this is not proof of direct PCI discovery/bind. The
checked source's BCMA PCI, SSB bridge, and brcmfmac direct tables lacked this
ID at the pinned revision. Bus/core path and calibration location remain
unknown. Wi-Fi can be omitted from initial Ethernet research but must not be
claimed supported. Never publish calibration data.

## 14. Vendor source provenance

See `docs/SOURCE-PROVENANCE.md`. Broadcom mirror:
`https://github.com/nomis/bcm963xx_4.12L.06B_consumer`, commit
`e2f23ddbb20bf75689372b6e6a5a0dc613f6e313`, a public mirror rather than
official Zyxel source. It includes exact boardparms text and family XTM code,
but exact build equivalence and redistribution rights are not established.
The source tree and proprietary blobs are not in this repository. Other
historical GPL archive leads are recorded there; an unavailable host does not
prove source does not exist.

## 15. Tasks Hermes CAN do without router

- Clone pinned upstream, apply patches, reproduce baseline/profile builds.
- Run DTS compile/round-trip, inspect DTB, and refine evidence-backed nodes.
- Analyze upstream b53, bcm63xx Ethernet, BMIPS NAND, image formats, and
  sibling-device commits.
- Continue public-source searches and provenance/licensing review.
- Port `bcmxtmrt` incrementally; classify 2.6-to-6.18 API changes and write
  narrow compatibility layers/compile probes.
- Reconstruct vendor ABI from sanitized symbol inventories; search for
  `adsldd`/`bcmxtmcfg` sources without asserting absence globally.
- Research Wi-Fi PCI/BCMA/SSB discovery and OpenWrt driver tables.
- Improve offline image parser, static analysis, tests, patch series, scripts,
  docs, and runtime test plans.
- Build candidate Ethernet topologies with confidence labels only; do not
  activate unproven configuration.
- Commit and push clean source/docs/patches.

## 16. Tasks that must not be marked PASS without router

OpenWrt boot; usable RAM; LAN link; DSA CPU port and physical jack mapping;
runtime BCM53125 ID; switch PHY links; Wi-Fi discovery/association/calibration;
DSL initialization/sync/stats; XTM netdev; PPP session and Internet routing;
USB functionality; hardware acceleration; NAND read/write/ECC behavior; CFE
handoff; stock recovery; factory image acceptance; sysupgrade; reboot soak;
factory-reset recovery. Label each `NEEDS-DEVICE` or `NOT-TESTED`.

## 17. Tasks requiring device owner later

After an independently completed offline safety review and explicit owner
authorization: benign boot/runtime validation, Ethernet jack map, DSL sync and
PPPoE, Wi-Fi association/calibration, performance, recovery-path validation,
and any eventual stock-web firmware validation. This handoff itself authorizes
none of those actions.

## 18. Current blockers

1. Exact BCM63168/BCM53125 switch topology and safe DSA mapping.
2. Exact NAND writer/slot/bad-block/ECC semantics and non-UART recovery path.
3. XTM forward-port's structural Broadcom dependencies; missing ADSL and XTM
   config source/objects.
4. Wi-Fi host/bus discovery and calibration path.
5. No device runtime evidence, by design.

## 19. Recommended next work

P0: maintain public-safe, reproducible repo and scripts.

P1: incremental `bcmxtmrt` Linux 6.18 port compile probes.

P2: exact `963168MXH_17A` Ethernet and switch topology.

P3: Broadcom image writer, dual-slot and WFI/bad-block behavior.

P4: source search and ABI reconstruction for `adsldd`/`bcmxtmcfg`.

P5: Wi-Fi PCI discovery.

P6: FAP/HNAT only after software-routing bring-up.

For DSL, compile after each small change and record the first meaningful error
class. Do not import Linux 2.6 headers wholesale or hide structural failures
with blanket warning suppression.

## 20. Evidence policy

Use labels from `docs/EVIDENCE-POLICY.md`: `LIVE-DEVICE`, `STOCK-BINARY`,
`STOCK-BOOT-LOG`, `EXACT-BOARD-SOURCE`, `FAMILY-SOURCE`, `UPSTREAM`,
`BUILD-RESULT`, `INFERENCE`, `UNKNOWN`. Cite revision/report/date. Keep compile
and runtime claims separate; keep exact-board and family-source evidence
separate. Preserve negative and failed-probe findings.

## 21. How to update STATUS.md

After each meaningful change, update the relevant status row, exact evidence,
runtime yes/no, and whether a device is needed. Use only evidence status from
the policy. Do not mark overall `READY-FOR-CONTROLLED-FLASH` until all defined
offline/device gates have evidence; even then do not flash. Current state stays
`PARTIAL-PORT`.

## 22. Handoff back to device-owning agent

Return a concise commit/patch summary, exact build/test commands and exit
status, new artifact hashes, evidence-label changes, remaining blockers, and
tests that still require physical hardware. Preserve a clean main branch or
provide a reviewable branch/PR. Never request device action implicitly; list
`NEEDS-DEVICE` tasks separately for owner review.
