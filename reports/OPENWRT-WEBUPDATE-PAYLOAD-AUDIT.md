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

## New blocker found: OpenWrt's BCM63xx imagetag parser refuses NAND

The SBG3300 DTS currently assigns `compatible = "brcm,bcm963xx-imagetag"` to
its `firmware` fixed partition (`target/linux/bmips/dts/bcm63168-zyxel-sbg3300-n000.dts:124-128`). But the matching generic parser
`target/linux/generic/files/drivers/mtd/mtdsplit/mtdsplit_bcm63xx.c:146-164`
starts with:

```c
if (mtd_type_is_nand(master))
    return -EINVAL;
```

So it never parses a Broadcom imagetag on this NAND device, regardless of
whether the compatible string is set. The OpenWrt kernel config also has
`CONFIG_MTD_SPLIT_FIRMWARE` unset, and this parser creates only kernel/rootfs
partitions from standard CFE addresses; it does not implement the ZyXEL
MSTC NAND `rootfs_update`/tag-block path. Thus the present DTS/profile does
not establish an OpenWrt rootfs split or mount path for this board. Turning on
the generic split config alone will not help: the parser explicitly rejects
NAND.

A next development gate is a dedicated read-only design/audit for rootfs
selection on NAND: either a custom parser for the actual SBG3300 NAND layout,
or a DTS/rootfs arrangement matching what the CFE/vendor kernel really exposes.
Do not patch a partition label by guess; establish tag-block offset, JFFS2 vs
SquashFS filesystem, `root=`/root-device selection and exact partition bounds
from the actual stock writer and kernel first. The current stock update path
places the tag at `rootfsAddr - TAG_BLOCK_LEN` and flashes the combined image
through `kerSysBcmImageSet`; that is not equivalent to the generic parser's
256-byte header splitting. No partition-layout patch or candidate image has
been created.

- The old claim that simply renaming the DTS partition to `rootfs` would fix
  selection is withdrawn. OpenWrt's auto-root hook does key off the name, but
  the stock MTD offset/rootfs mapping and expected filesystem remain unknown;
  that rename could select the wrong range or wrong data as `/`.

- Complete JFFS2 payload in the exact stock writer layout, with verified boot
  files and correct kernel/root arrangement.
- CFE-facing boot-file arrangement and correct CFE RAM component; finding
  `cferam.000` in stock does not prove a replacement image boots or authorize
  any CFE modification.
- Compatibility of OpenWrt kernel/rootfs with this SBG3300 CFE/flash path,
  including partition writes, tag sequence, slot selection and kernel entry.
The stock kernel's rootfs contract is still unresolved: stock exposes a partition named
`rootfs`; the current OpenWrt DTS declares a `firmware` partition, which neither
splits nor configures a root device. The standard parser configured by that
`compatible` rejects NAND. A dedicated rootfs strategy (fix the NAND partition
model/parser or prove CFE boots the kernel with an embedded initramfs) is a
separate blocker before any image packaging. The CFE loader support is not a
licence to modify CFE; any proposed route must remain read-only and fully
verified before consideration.
## Rootfs selection: source-backed next gate (no DTS patch yet)

OpenWrt 6.18's generic MTD splitter path is not the answer for this board:

- SBG3300 DTS sets `compatible = "brcm,bcm963xx-imagetag"` on its NAND
  `firmware` partition, `target/linux/bmips/dts/bcm63168-zyxel-sbg3300-n000.dts:124-128`.
- OpenWrt's MTD split support invokes the `firmware` parser only when that
  partition has no `compatible`, `target/linux/generic/pending-6.18/400-mtd-mtdsplit-support.patch:208-212`.
- Regardless, `target/linux/generic/files/drivers/mtd/mtdsplit/mtdsplit_bcm63xx.c:146-154`
  explicitly returns `-EINVAL` for NAND. That parser is for BCM63xx NOR, not
  SBG3300 NAND.
- Linux kernel root selection consumes `root=` (`kernel/linux/init/do_mounts.c:147-153,385-395`); OpenWrt's special auto-root sets `ROOT_DEV` only for an
  MTD partition named `rootfs` or marked `linux,rootfs`
  (`target/linux/generic/hack-6.18/420-mtd-support-OpenWrt-s-MTD_ROOTFS_ROOT_DEV.patch:19-24`). The present DTS calls the partition `firmware` and has no
  `linux,rootfs`; current config has `CONFIG_MTD_ROOTFS_ROOT_DEV=y` but this
  name test will not select it.

A DTS-only rename to `rootfs` might let OpenWrt's generic root-device hook
select that MTD partition, but is **not yet a safe fix**: it doesn't split
kernel/rootfs, prove the partition contents match the expected filesystem, or
establish the correct physical region. Do not edit DTS until the stock
kernel's MTD mapping and root mount contract are explained.

## Stock update path offset evidence (family source only)

The vendor BCM 4.12 source distinguishes the tag block from the logical
filesystem address:

- `board.c:2457` computes `rootfsOffset = rootfsAddr - IMAGE_BASE -
  TAG_BLOCK_LEN`; `TAG_BLOCK_LEN` is 128 KiB on NAND (`bcmTag.h:47-51`).
- `board.c:2567-2579` raises rootfs/kernel addresses to
  `flash_rootfs_start_offset` if needed; then `2581-2582` applies `BOOT_OFFSET`.
- `board.c:2707-2709` calls `kerSysBcmImageSet(rootfsAddr-TAG_BLOCK_LEN,
  tagFs, newImgSize)`, writing the tagged logical image from one NAND tag block
  before the declared rootfs address.
- `bcm63xx_flash.c:277-279` initializes `flash_rootfs_start_offset` to
  first sector size, with a floor at `FLASH_LENGTH_BOOT_ROM`; its exact value
  for SBG3300's production config must be established before equating that
  address with the live `mtd0 rootfs` partition start. The matching stock
  **kernel MTD partition parser** is absent from the extracted stock-kernel evidence here.

Slot-specific evidence in the inspected family source:

- `board.c:getTagFromPartition()` (2110-2210) reads slot 1 from the block at `flash_rootfs_start_offset`; slot 2 from half-flash. It corrects a tag with too-low `rootfsAddress` to `(actual_tag_block + 1) * erase_size + IMAGE_BASE` (2190-2205), so the tag read from installed flash can differ from the downloaded file template.
- `getBootImageTag()` (2240-2320) chooses the booted tag using NVRAM bootline `p=` and sequence numbers (2252-2295).
- During an update when the current and replacement fit half-flash and current slot is 1, the writer selects slot 2 (2635-2682): `offset = totalSize/2 + TAG_BLOCK_LEN`; then writes `rootfsAddress = IMAGE_BASE + offset` (2679-2681). At 128 MiB that is tag address `0xc3c20000`; the vendor NAND parser formula translates it to `0x04020000`, matching the sanitized live rootfs MTD start. Slot 1 template `0xbfc40000` translates to `0x00040000`.

This reconciles the arithmetic **within the family source model**: downloaded stock file is slot-1 template; live MTD extent corresponds to slot 2, plausibly because the router is booted from that slot. It does **not** prove the exact 2018 production binary used this mirror, or directly reveal the current live booted slot/tag, sequence, bad-block adjustments, or write behavior. Do not use the correspondence to change DTS or build a wrapper without exact-build confirmation.



The inspected stock source does not yet reconcile to the live partition map. For the downloaded stock tag, `rootfsAddress` at tag offset `0x5e` is decimal `3217293312` = `0xbfc40000`; with the family header's `IMAGE_BASE=0xbfc00000`, `FLASH_BASE=0xb8000000` and `BOOT_OFFSET=FLASH_BASE-IMAGE_BASE`, the `bcm63xx-nand.c:215` expression `rootfsAddress + BOOT_OFFSET - FLASH_BASE` evaluates to `0x00040000`. The live kernel reports `rootfs` at `0x04020000`. Difference is exactly `0x04000000` (64 MiB). So this tag specimen plus this family-source formula is not enough to claim the source predicts the live active slot; possible active-slot/tag adjustment, compile-time address mapping, bad-block handling, or source/build mismatch remains unresolved. This directly rules out relying on the earlier tentative assumption that the 2018 running MTD start follows from the tag. Do not patch DTS based on either value until the active tag/partition formula from the exact running build is recovered.

## Next experiment (offline only)

1. Recover/identify the exact stock 2018 kernel partition parser / mount code
   from the extracted files and available source references; establish whether
   MTD partition offsets include/exclude the tag block.
2. Trace OpenWrt's fixed-partition creation and `ROOT_DEV` selection with its
   current DTS/config; if sufficient, propose a minimal DTS-only patch (no
   image generation) and a unit test proving only the intended MTD rootfs is
   selected. Build the DTB and inspect the resulting partition table offline.
3. Separately confirm whether the intended filesystem is SquashFS or JFFS2 and
   whether OpenWrt's rootfs can fit in the verified logical rootfs budget.
4. Only after those facts pass should rootfs packaging be planned; never make a
   valid MSTC wrapper, flash/upload, or claim bootability.

Stock `.bin`: static-code-compatible by analysis; observed web acceptance
`NOT-TESTED`.

OpenWrt initramfs ELF and sysupgrade TAR: rejected as stock Web Update
containers. No wrapper or candidate generated: existing outputs are not a
complete bootable payload, and a valid-looking wrapper could authorize writing.

- The same static audit reports 761 newc records and confirms embedded `init`,
  `sbin/init`, `bin/busybox`, `etc/preinit`, and `sbin/procd`; regression tests
  focused initramfs tests pass (2/2); full repository suite passes (37/37).
- Static CPIO presence does not prove CFE load, DTB handoff, hardware boot or runtime; `NOT-FLASHABLE` remains.
