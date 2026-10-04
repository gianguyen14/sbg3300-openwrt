# Upstream bmips baseline build

- Upstream: `https://github.com/openwrt/openwrt.git`
- Branch/commit: `main`, `5edcc1c43cb97048b506168fbbe00538956796d6`
- Target selection: `bmips/bcm63268`, generic `Default` profile
- Configuration: `configs/sbg3300_defconfig`, then upstream `make defconfig`
- Checkout: `/home/nguyen/openwrt-sbg3300` (space-free symlink to the physical
  checkout)
- Build command: `make -j3 V=s`
- Log: `/tmp/sbg-openwrt-bmips-baseline-build.log`

## Status

The build is running again after its first attempt spent over an hour on slow
GNU mirror transfers. That attempt was interrupted during GCC/GDB downloads;
both archives were fetched from an alternate GNU mirror and matched the exact
SHA256 values required by OpenWrt before resuming:

- GCC 14.4.0: `752b6f567beac83159c77a7680b1316bdd784738bff9a9d070112c09da90f6d9`
- GDB 16.3: `bcfcd095528a987917acf9fff3f1672181694926cc18d609c99d0042c00224c5`

As of 2026-10-04 14:08 +07, the resumed `make -j3 V=s` has compiled the
unmodified bcm63268 kernel and is building host/target packages. `vmlinux` is
ELF32 MIPS big-endian, o32, with MIPS32 flags (entry `0x80896f50`), 58,412,552
bytes, SHA256
`04ca95b76fe03c6a6de3fc86e29ee0d7eb522f4ec2cc21b8700f0e3aaa64ab9b`.
The full baseline build remains active; no image or overall PASS result exists
yet. Earlier
interrupted-attempt errors remain in the combined log, so final success will
be determined from the resumed process exit status and its final log lines,
not from a broad grep of historical errors. This is an unmodified upstream
baseline; SBG3300 DTS or image changes have not been applied to this checkout.

The baseline `vmlinux` has been copied to
`builds/upstream-bmips-bcm63268-baseline/vmlinux` before any port build can
overwrite the OpenWrt work directory. A reference
`bcm63268-comtrend-vr-3032u.dtb` from the same unmodified build is archived in
the adjacent `dts/` directory. These artifacts are ignored local build output,
not firmware images.

This baseline is offline-only and is not a boot or flash validation.
