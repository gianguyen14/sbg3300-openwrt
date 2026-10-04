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

The build is still running. The host-tool phase is compiling dependencies;
there is no completed target image or PASS result yet. Compiler warnings from
upstream host dependencies have appeared, but no fatal failure has been
observed. This remains an unmodified upstream baseline; SBG3300 DTS or image
changes have not been applied to this checkout.

This baseline is offline-only and is not a boot or flash validation.
