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

As of 2026-10-04 13:53 +07, the resumed `make -j3 V=s` has completed target
toolchain setup and moved on to unpack/prepare the Linux 6.18.54 bmips kernel.
The process remains active; no completed target image or PASS result exists.
Earlier
interrupted-attempt errors remain in the combined log, so final success will
be determined from the resumed process exit status and its final log lines,
not from a broad grep of historical errors. This is an unmodified upstream
baseline; SBG3300 DTS or image changes have not been applied to this checkout.

This baseline is offline-only and is not a boot or flash validation.
