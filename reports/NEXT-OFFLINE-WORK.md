# What to do next — offline OpenWrt payload development

Current boundary: the stock web-validator is reverse-engineered and tested
against the stock image. Existing OpenWrt artifacts are not stock-update
containers and do not form a complete boot payload. No MSTC wrapper has been
created; this is deliberate, because a valid tag could pass the router's
validator and authorize destructive writes.

Rootfs selection is not yet fixed; the interim recommendation to rename the DTS partition to `rootfs` is withdrawn pending the stock partition parser/offset proof. The standard imagetag splitter still rejects NAND, and the CFE RAM boot path is only plausible from the ELF format, not proven. See `OPENWRT-WEBUPDATE-PAYLOAD-AUDIT.md`. Next work: identify the exact stock 2018 NAND MTD partition/root mount parser, resolve `TAG_BLOCK_LEN` and `BOOT_OFFSET` relative to `/proc/mtd`, then decide a non-writing DTS/rootfs strategy. No wrapper, DTS change, or image candidate has been created; keep `NOT-FLASHABLE`.

1. Resolve the stock parser mapping first: exact NAND partition parser and the
   relationship between tag-block offset, BOOT_OFFSET, and live /proc/mtd.
   Do not rename the OpenWrt fixed partition until this is established.
2. Trace OpenWrt's fixed-partition creation and ROOT_DEV selection in source;
   if evidence suffices, propose a minimal DTS-only patch (no image generation)
   and offline DTB/partition test.
3. Confirm the filesystem type expected by the stock kernel and whether a
   custom NAND rootfs split/mount path is appropriate. Separately verify the
   OpenWrt root contents/init system against that mount path.
4. Determine from reliable exact-board CFE docs/source whether the initramfs
   ELF can be loaded into RAM; do not suggest UART or unverified TFTP/HTTP
   recovery.
5. Only after these facts pass, calculate the flash budget and plan payload
   packaging. Never create a valid MSTC wrapper or upload/flash under current
   constraints.


The initramfs ELF is self-contained at the Linux initramfs layer, but whether this exact CFE can load that ELF and the required memory/entry contract remain unverified; it is not a confirmed safe boot path.

## Current verified outputs

- initramfs ELF: 6,076,800 B, MIPS BE; RAM/CFE boot unverified.
- sysupgrade TAR: 6,390,038 B; members CONTROL, kernel (3,538,944 B), root
  SquashFS (2,844,672 B); not a Zyxel Web Update file.
- intermediate 5 MiB JFFS2: 865 valid nodes, dirents `1-openwrt`, `2-openwrt`,
  `vmlinux.lz`; no `cferam.000`, no whole rootfs.
- tests: OpenWrt project tests pass 32/32.

## Stop conditions

Stop before any image wrapping if the stock kernel mount/rootfs contract cannot
be established from source/log evidence, if CFE/JFFS2 requirements are
ambiguous, or if rootfs plus kernel exceeds the verified write budget. Do not
solve a mismatch by guessing image offsets, copying stock binaries/credentials,
or adding a valid tag around incomplete data.
