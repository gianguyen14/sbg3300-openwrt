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

This validates patch application, style, DTS syntax, and profile selection.
The OpenWrt kernel/image compile is still pending. Per-commit mail-format
checks report missing `Signed-off-by` metadata because these are local research
commits, not submitted upstream contributions; no sign-off is fabricated.
Nothing here demonstrates board boot, switch port mapping, NAND write safety,
DSL, or Wi-Fi operation.
