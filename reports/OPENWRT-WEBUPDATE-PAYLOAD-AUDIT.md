# OpenWrt image audit — offline, no wrapper generated

Date: 2026-10-18

## Scope and result

Read-only inspection of local OpenWrt target output and recipe against stock
`V1.01(AADY.9)C0.bin` and `UPGRADE-RECIPE.md`. No device access, image
construction, upload, flash, or sysupgrade was performed.

Result: do not wrap existing output into an MSTC image. A correctly tagged
container could pass the server-side gate and then be written; a valid-looking
wrapper is not a harmless test artifact. Current files have incompatible
containers/layouts and do not make a complete CFE/JFFS2 boot set.

## Local outputs verified

OpenWrt tree `/home/hermes/sbg3300-openwrt/test_port/openwrt`:
HEAD `ce87595bef57b4662fcc756aee3fdfd578c8ab42`; worktree clean.

1. `bin/targets/bmips/bcm63268/openwrt-bmips-bcm63268-zyxel_sbg3300-n000-initramfs.elf`
- 6,076,800 bytes, SHA256 `878d3f7875711e3db876bb4c27fa1fa9bbcd5a6531ee2d9dfa80c443c68b141d`.
- `file`: ELF 32-bit MSB, MIPS-I, statically linked; begins `7f 45 4c 46`,
  not an MSTC tag-v6 update container.
- Initramfs ELF; CFE/RAM boot on this board unverified.

2. `bin/targets/bmips/bcm63268/openwrt-bmips-bcm63268-zyxel_sbg3300-n000-squashfs-sysupgrade.bin`
- 6,390,038 bytes, SHA256 `da50aaa1700c0322aedb07208fe9666323f700355afaa46d69e1bf69b3a5a969`.
- GNU tar: `CONTROL` 25 B, `kernel` 3,538,944 B, `root` 2,844,672 B
  (SquashFS). OpenWrt sysupgrade format, not Zyxel stock Web Update.

3. Intermediate
`build_dir/target-mips_mips32_musl/linux-bmips_bcm63268/tmp/openwrt-bmips-bcm63268-zyxel_sbg3300-n000-squashfs-cfe.bin.kernel`
- 5,242,880 bytes, JFFS2 big-endian. Valid-node scan found 865 nodes and
  three dirents: `1-openwrt` (ino 2), `2-openwrt` (ino 3), `vmlinux.lz` (ino 4).
  No `cferam.000`, no complete root filesystem.
- `vmlinux.lz` logical length 3,424,011 bytes. This is an intermediate, not a
  complete firmware image.

Build recipe:
- `target/linux/bmips/image/Makefile:326-346` (`Device/bcm63xx-nand`):
  `KERNEL := kernel-bin | append-dtb | relocate-kernel | lzma | cfe-jffs2-kernel`,
  `KERNEL_INITRAMFS := kernel-bin | append-dtb | lzma | loader-lzma elf`,
  `IMAGE/sysupgrade.bin := sysupgrade-tar | append-metadata`; default cfe image
  recipe composes append-kernel, `cfe-jffs2-cferam`, append-ubi and cfe-wfi-tag.
- `target/linux/bmips/image/bcm63268.mk:3-17`: SBG3300 inherits NAND base,
  sets CHIP_ID/SOC and NAND geometry; profile does not define a verified Zyxel
  MSTC factory/Web Update image or provide matching `CFE_RAM_FILE`.

## Stock/device size nuance

Stock tag declares 23,724,032 (`0x16a0000`) payload bytes starting at file
offset `0x20000`, ending `0x16c0000`. Observed `rootfs` MTD size is also
`0x16a0000`, erase size `0x20000`. Equal numbers do not prove the file payload
maps byte-for-byte to that partition: the stock file has tag block and 21,601 B
trailer, and writer can inject NVRAM and account for bad blocks/slots. Do not
pad/relabel OpenWrt outputs to force this length.

## Missing boot requirements

- Complete JFFS2 payload in the exact stock writer layout, with verified boot
  files and correct kernel/root arrangement.
- CFE-facing boot-file arrangement and correct CFE RAM component; finding
  `cferam.000` in stock does not prove a replacement image boots or authorize
  any CFE modification.
- Compatibility of OpenWrt kernel/rootfs with this SBG3300 CFE/flash path,
  including partition writes, tag sequence, slot selection and kernel entry.
- Safe offline candidate validation that does not submit the candidate to a
  writer. Static tag/CRC checks cannot establish bootability or write safety.

## Disposition

Stock `.bin`: static-code-compatible by analysis; observed web acceptance
`NOT-TESTED`.

OpenWrt initramfs ELF and sysupgrade TAR: rejected as stock Web Update
containers. No wrapper or candidate generated: existing outputs are not a
complete bootable payload, and a valid-looking wrapper could authorize writing.

Hardware bootability / flash safety: `NOT-VERIFIED / NOT-FLASHABLE`.
