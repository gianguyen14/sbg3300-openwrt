# Board patch validation

Date: 2026-10-04
Base: OpenWrt `5edcc1c43cb97048b506168fbbe00538956796d6`
Port branch: `zyxel-sbg3300-port`

- The final aggregate patch applies cleanly in `git apply --check` against the
  pinned, clean upstream checkout.
- The aggregate source diff passes upstream `scripts/checkpatch.pl
  --no-tree --strict` with zero warnings and zero errors.
- The standalone DTS compiled and round-tripped earlier; see
  `reports/DTS-BUILD.md`.
- The selected device/profile symbol resolves through upstream `make defconfig`;
  see `reports/PROFILE-CONFIG.md`.
- The four-patch series, including the no-UART-console DTS change, applies via
  `git am` to a fresh detached worktree at the pinned base. Aggregate diff
  check is clean and `scripts/checkpatch.pl --no-tree --strict` reports zero
  warnings and zero errors (75 lines checked).
- The custom SBG3300 initramfs profile subsequently completed a full offline
  build; see `reports/SBG3300-OFFLINE-INITRAMFS.md`.

This validates patch application, style, DTS syntax, profile selection, and
offline compilation. Per-commit mail-format
checks report missing `Signed-off-by` metadata because these are local research
commits, not submitted upstream contributions; no sign-off is fabricated.
Nothing here demonstrates board boot, CFE image compatibility, switch port
mapping, NAND write safety, DSL, Wi-Fi, or runtime operation.
