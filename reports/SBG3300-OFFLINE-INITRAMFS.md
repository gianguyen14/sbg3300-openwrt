# SBG3300 offline initramfs build

Date: 2026-10-04

## Build provenance

- Upstream: `https://github.com/openwrt/openwrt.git`
- Pinned base: `5edcc1c43cb97048b506168fbbe00538956796d6`
- Local port branch: `zyxel-sbg3300-build`, commit
  `18c17336871e73ddfbab3198104d8c42df844146` (research patch series; not an
  upstream commit)
- Kernel: Linux `6.18.54`, bmips `bcm63268`
- Profile: `zyxel-sbg3300-n000`, research-only skeleton
- Command: `make -j3 V=s`
- Result: exit status 0 after correcting the DTS `/chosen` merge
- Full build log: `/tmp/sbg3300-port-full-rebuild.log` (local, not committed)

## Produced files

Local-only artifacts are archived under
`builds/sbg3300-offline-initramfs/` and verified against that directory's
`SHA256SUMS`.

| Artifact | Size | SHA256 |
|---|---:|---|
| `openwrt-bmips-bcm63268-zyxel_sbg3300-n000-initramfs-OFFLINE-ONLY.elf` | 5,925,020 | `3961a39d5d554ce467b9575bbc6f6293d385ddda9fc4dc9b3dbf0c3cf8027b51` |
| `dts/image-bcm63168-zyxel-sbg3300-n000.dtb` | 9,736 | `e6e680e875e0f1251eb7d3c2f355acc2dc94e2bc909aa1d5fff2af5a4baa90fb` |

The build emitted only the SBG3300 initramfs loader ELF and package manifest
for this profile. No SBG3300 factory or sysupgrade image was generated.

## Static checks

- `file`: ELF32, MIPS big-endian, statically linked.
- `readelf -h`: ELF32, MIPS R3000 machine tag, entry `0x81000000`, one load
  segment. This is OpenWrt's relocated initramfs loader format; these ELF
  attributes do not prove the SBG3300 CFE can load it.
- `binwalk`: LZMA-compressed payload is present in the ELF.
- DTB model: `Zyxel SBG3300-N000 (research-only skeleton)`.
- DTB compatibles: `zyxel,sbg3300-n000`, `brcm,bcm63168`, `brcm,bcm63268`.
- DTB `/chosen/bootargs` and `/chosen/stdout-path` are empty, clearing the
  inherited early console selection. No UART/JTAG was used.
- DTB keeps BMIPS `memory@0 reg = <0 0>` discovery behavior; it does not assert
  the whole physical RAM range as usable memory.
- DTB includes SoC NAND controller and observed geometry/ECC properties, but
  has no partition map. Presence in a compiled DTB is not proof that the
  controller's ECC/OOB layout or write behavior matches this exact board.
- Ethernet remains disabled; this build does not establish LAN connectivity,
  DSA topology, or switch support.

## Limits and disposition

This artifact is `OFFLINE-ONLY` and `NOT-FLASHABLE`. It is not wrapped in a
Zyxel/Broadcom image header, has not passed the stock updater validator, is not
proven compatible with the CFE handoff, and has not booted on hardware. The
physical NAND map, bad-block translation, safe fallback/recovery route,
Ethernet/switch mapping, DSL/XTM, and Wi-Fi remain unresolved or unvalidated.
No router state was changed for this build.
