# Upstream bmips baseline build

- Upstream: `https://github.com/openwrt/openwrt.git`
- Branch/commit: `main`, `5edcc1c43cb97048b506168fbbe00538956796d6`
- Target selection: `bmips/bcm63268`, generic `Default` profile
- Configuration: `configs/sbg3300_defconfig`, then upstream `make defconfig`
- Checkout: the original host used a space-free alias; reproduce with the
  portable instructions in `REPRODUCE.md` and `tools/prepare-openwrt.sh`.
- Build command: `make -j3 V=s`
- Log: `/tmp/sbg-openwrt-bmips-baseline-build.log`

## Status

The first attempt spent over an hour on slow GNU mirror transfers and was
interrupted during GCC/GDB downloads. Both archives were then fetched from an
alternate GNU mirror and matched the exact SHA256 values required by OpenWrt:

- GCC 14.4.0: `752b6f567beac83159c77a7680b1316bdd784738bff9a9d070112c09da90f6d9`
- GDB 16.3: `bcfcd095528a987917acf9fff3f1672181694926cc18d609c99d0042c00224c5`

As of 2026-10-04 14:08 +07, the resumed `make -j3 V=s` has compiled the
unmodified bcm63268 kernel and is building host/target packages. `vmlinux` is
ELF32 MIPS big-endian, o32, with MIPS32 flags (entry `0x80896f50`), 58,412,552
bytes, SHA256
`04ca95b76fe03c6a6de3fc86e29ee0d7eb522f4ec2cc21b8700f0e3aaa64ab9b`.
The unmodified baseline completed successfully: `tools/build-openwrt.sh baseline`
returned exit code 0 and printed `Built unmodified upstream baseline` at the
pinned commit. It produced the default profile manifest and factory/
sysupgrade images for existing bcm63268 devices. It did not contain the
SBG3300 DTS/profile. Earlier interrupted-attempt errors and benign Kconfig
recursive-dependency warnings from unrelated video/telephony feeds remain in
the combined log; the completed build command's exit status is 0. The output is
an offline baseline, and sibling device images are not for the SBG3300.

The baseline `vmlinux` has been copied to
`builds/upstream-bmips-bcm63268-baseline/vmlinux` before any port build can
overwrite the OpenWrt work directory. A reference
`bcm63268-comtrend-vr-3032u.dtb` from the same unmodified build is archived in
the adjacent `dts/` directory. The kernel `.config` is archived as
`builds/upstream-bmips-bcm63268-baseline/kernel.config` (SHA256
`2e25ed22442c4c71dab98accc62f82f9ff35a0c4d231527c8726c50d67cf70a4`); it has
`CONFIG_CPU_BMIPS4350=y`, `CONFIG_SMP=y`, two CPU slots, and o32 enabled. These
are compile-time target settings, not runtime core/board confirmation. These
artifacts are ignored local build output, not SBG3300 firmware images. The
artifact manifest currently verifies all 28 files in the baseline build
directory. `tools/build-openwrt.sh` now excludes its checksum file from the
hash input; an earlier self-hash entry was discarded and regenerated, then all
28 entries passed `sha256sum -c`.

This baseline is offline-only and is not a boot or flash validation.
