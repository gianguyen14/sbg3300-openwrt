# SBG3300-N000 OpenWrt full port (R&D)

This is an isolated research project for a native OpenWrt port to the Zyxel
SBG3300-N000. It does not replace the currently working stock-custom router.
No generated image is approved for installation unless all gates in
`FLASH-SAFETY.md` pass and the user explicitly authorizes installation.

## Current state

- Project status: `RESEARCHING`.
- Upstream source: official `openwrt/openwrt`, branch `main`; checkout and commit
  are recorded in `STATUS.md` and `reports/upstream-source.txt`.
- Baseline device family: `bmips/bcm63268`; upstream already has BCM63168 board
  definitions for Actiontec T1200H and Sagemcom F@ST 3864 OP.
- SBG3300-specific DTS/image definition: research skeleton only. Board GPIO,
  switch wiring, physical NAND map, and boot container are not established yet.
- DSL: stock image uses proprietary BCM63168D0 ADSL/XTM modules and PHY firmware;
  current-kernel source compatibility has not been demonstrated.
- All output images, if built, are offline artifacts and not flashable.

## Source layout

The OpenWrt checkout is exposed at `source/openwrt` as a symlink. Upstream's
build system refuses paths containing spaces, so its physical checkout is at
`/home/nguyen/sbg3300-openwrt-source`; build via the alias
`/home/nguyen/openwrt-sbg3300`.

Stock firmware, extracted rootfs and the STABLE-V1 snapshot are local-only and
excluded from Git. They contain device/firmware material and must remain
permission-restricted. Do not add PPP credentials, NVRAM dumps, MAC addresses,
private keys, or user tokens to source control.

## First safe workflow

1. Review `STATUS.md`, `HARDWARE.md`, and `NAND-MAP.md`.
2. Build an unmodified upstream bmips baseline before applying SBG3300 patches.
3. Keep DTS properties evidence-backed; unknown values stay TODO.
4. Build initramfs/static artifacts first. Do not create a stock-updater wrapper
   until the complete image layout and writer behavior are proven.
5. Never flash automatically. See `FLASH-SAFETY.md`.

This repository intentionally separates OpenWrt port research from the current
stock-custom/security-v1 installation.
