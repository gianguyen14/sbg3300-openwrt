# What to do next — offline OpenWrt payload development

Current boundary: the stock web-validator is reverse-engineered and tested
against the stock image. Existing OpenWrt artifacts are not stock-update
containers and do not form a complete boot payload. No MSTC wrapper has been
created; this is deliberate, because a valid tag could pass the router's
validator and authorize destructive writes.

Rootfs selection is still a blocker: stock uses a partition named `rootfs`; the current OpenWrt DTS declares `firmware`, while the configured generic imagetag parser rejects NAND and does not establish a root device. Do not wrap the OpenWrt outputs until a safe rootfs strategy is proven (custom NAND split/mount path or verified CFE loading of the initramfs). Do not modify CFE.

Build a complete *offline-only* candidate root filesystem and prove it fits the
stock partition/layout before touching the image container. Start with the
existing OpenWrt squashfs root, not the sysupgrade tar as a whole. Determine
whether the SBG3300 CFE/vendor kernel can directly mount that filesystem:

1. Read the exact stock kernel command line/mount path and MTD partition map
   from prior sanitized evidence, vendor source, and stock init files. Current
   evidence: stock `/etc/fstab` only mounts `/data` as JFFS2; kernel chooses
   root filesystem from image/tag/kernel arguments. Do not infer that SquashFS
   in OpenWrt is mountable merely because the kernel has SquashFS enabled.
2. Check OpenWrt target kernel config: JFFS2 and SquashFS are enabled, but
   `CONFIG_MTD_SPLIT_FIRMWARE` is disabled. Verify exact MTD/rootfs detection
   and `/dev/root`/root= behavior against its DTS and target patches.
3. Compare OpenWrt rootfs contents/init system with stock boot requirements.
   Stock init is BusyBox `/sbin/init` and `/etc/init.d/rcS`; OpenWrt uses
   procd/preinit. Check the kernel's actual initramfs ELF root and sysupgrade
   `root` member offline. Keep dependencies/config out; do not transplant the
   stock `/sbin/init`, libraries, web daemon, proprietary modules, or user data.
4. Determine whether the stock updater's JFFS2 writer preserves erased-block
   boundaries and how it loads the kernel: read-only vendor code + stock
   extraction; verify `cferam.000`, `vmlinux.lz` naming, load/entry fields,
   compression stream and sequence/slot handling. Do not modify or substitute
   CFE content.
5. Calculate an exact image budget from the confirmed stock writer and MTD
   boundaries. Current coincidence: stock tag payload length and rootfs MTD
   size are both 0x16a0000, while the stock container payload begins at file
   offset 0x20000. This is not a mapping proof; do not pad to that size.
6. Only after gates 1-5 pass, create an inert local rootfs/layout test with no
   valid MSTC tag or valid CRC, then test the layout with parsers/unit tests.
   Never make a Web-validator-valid image until the payload is proven bootable;
   never upload/flash under current safety constraints.

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
