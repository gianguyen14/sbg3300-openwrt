# What to do next — offline OpenWrt payload development

Current boundary: the stock web-validator is reverse-engineered and tested
against the stock image. Existing OpenWrt artifacts are not stock-update
containers and do not form a complete boot payload. No MSTC wrapper has been
created; this is deliberate, because a valid tag could pass the router's
validator and authorize destructive writes.

The stock image tag is a slot-1 template, not proof of the live active slot. In the inspected Broadcom family updater, when current image fits slot 1 and replacement fits half-flash, the inactive-slot path sets the next rootfs offset to `(totalSize/2) + TAG_BLOCK_LEN`; with total flash `0x08000000`, that is `0x04020000`. The family BSP's inactive-slot formula produces the live rootfs start (0x04020000), but that is only arithmetic corroboration. The downloaded tag is slot-1 (0xbfc40000); exact 2018 active-tag/build equivalence and bad-block behavior remain unproven. Do not patch DTS on this inference. Keep any DTS mapping conditional on this slot path and the exact MTD layout; no source change yet.

1. Resolve the stock parser mapping first: exact NAND partition parser and the
   relationship between tag-block offset, BOOT_OFFSET, and live /proc/mtd.
   Family source plus arithmetic suggest the inactive-slot formula can match the
   live rootfs start, but exact 2018 active-tag/build equivalence remains
   unverified; do not rename the OpenWrt fixed partition or wrap an image yet.
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


The initramfs ELF artifact has entry `0x81000000`, one LOAD segment at that address, one read-only segment, and a newc CPIO archive in the linked kernel blob. The CPIO build input includes complete root; static scan validates 761 records including init/procd. But `loader-lzma elf` is a BMIPS loader pipeline, and there is no evidence CFE on this exact board accepts arbitrary ELF program headers. Treat as static-only, not RAM-boot-capable.

- Stock tag/parser relationship: slot 1 template maps to `0x40000`; family BSP
  inactive-slot write formula maps slot 2 to live MTD `0x4020000`. This is
  arithmetic/source corroboration only; exact 2018 build and live booted tag
  are not confirmed. No guessed DTS change.
- `tools/audit-stock-rootfs-offset.py` reproduces both translations from exact
  stock tag and family constants. Its test asserts the arithmetic, not router
  state.
- Full test suite: 37/37 pass; `git diff --check` clean at last verification.
- No wrapper/candidate was created. Maintain `NOT-FLASHABLE`.


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
