# Pre-final source publication review

Scope: source changes on feat/sbg3300-pre-final-integration, stacked on the
reviewed XTM feature branch. Source approval does not establish hardware support
or final firmware readiness. All generated .ko/APK/ELF, complete compiler logs,
private signing keys, stock firmware and local vendor mirrors remain outside Git.

| Files | Provenance/license and publication decision |
|---|---|
| drivers/ethernet/enetsw_contract.h; tests/test_enetsw_contract.c; tools/test-enetsw-contract.sh | Original GPL-2.0-or-later input/IRQ/resource policy and tests. Approved; same header used by the compiled driver |
| integration/schema-patches/0003; OpenWrt patch 0009 | Original changes to pinned upstream GPL-2.0-or-later enetsw driver. Existing copyright/author metadata retained. Approved GPL patch, no vendor mirror body |
| integration/bindings/* | Original GPL-2.0-only OR BSD-2-Clause schemas documenting actual pinned driver properties; no hardware topology/firmware/calibration fixture. Approved |
| integration/schema-patches/0001 and 0002; OpenWrt 0006/0008 | Original deltas to GPL/BSD upstream schemas, including exact identity chain and actual field types. Existing notices/constraints retained; no scanner weakened. Approved |
| integration/dts/*; OpenWrt 0005/0007; series | Original safe board changes and exact-family resource facts. All unknown SAR/network/storage topology inactive. Existing SoC mappings corrected from pinned driver/binding evidence. Approved |
| integration/openwrt/*; tools/stage-xtm-package.sh | Original GPL-2.0-only package/staging logic; module source copied from one public implementation only, no autoload/firmware. Approved |
| configs/kernel-pre-final.fragment; configs/sbg3300-pre-final.config | Plain original compile configurations without credentials or private device values. Approved |
| tools/build-pre-final-kernel.sh; validate-pre-final-dts.sh; audit-kernel-artifacts.py; check-offline-dtb.py; test-contracts-mips.sh | Original GPL-2.0-only build/inspection/CPU-test code. No router commands. Regular files only in artifact/DTB readers. Approved |
| tests/test_kernel_artifacts.py; tests/test_offline_dtb.py | Original GPL-2.0-only rejection tests with synthetic software data, no private binary/device values. Approved |
| Existing build/prepare helper updates | Reviewed exact source-tree acceptance and real PTM source staging. Existing per-file licenses preserved. Approved |
| Reports/status/handoff/docs and artifact TSVs | Original explanatory text/factual measurements; binaries and raw device data excluded. Approved |

The top-level Apache license does not override GPL components. GPL COPYING and
upstream source attributions are retained. This work is source-informed original
implementation and GPL upstream patching, not a claimed clean-room process.
Vendor-derived material with unsettled rights was not copied into this branch.

The local scanner is conservative and unchanged. Legitimate published upstream
copyright/author contact metadata may still produce contact-email review findings
in patch context; such attribution is reviewed and retained, never removed to
make the scan appear clean. No owner credentials, MAC/serial/calibration/NVRAM,
stock binary, private key/token/cookie or unlicensed vendor implementation occurs
in the new public files. Final scan counts/findings and reachable-history review
are recorded at the publication milestone.

## Staged source/history scan milestone

Local scan: 114 tracked files, 346 reachable Git objects. Review findings are
only one contact-email match in each of the two copies of the upstream enetsw
patch. Both are the preserved, publicly published upstream MODULE_AUTHOR
attribution, not device/owner data or credentials. Manually reviewed and
approved to retain that attribution. Scanner exit 1 is recorded honestly; its
patterns and exclusions were not changed. New files were reviewed individually;
no proprietary/secret/device material was found.

The unmodified Git whitespace checker reports 271 diagnostics in
new textual patch payloads (unified-diff context prefixes before tabs/blank
lines, including nested Linux patches). These are reviewed format requirements,
not whitespace defects in applied source. Non-patch staged files and the actual
applied OpenWrt source diff pass diff --check. No Git whitespace attributes,
scanner patterns or validation rules were disabled. The raw nonzero checker
result is retained in the local project-patch-format-whitespace.log.

Final follow-up scan before report commit: 115 tracked files, 403 reachable
objects, with only the same two upstream MODULE_AUTHOR contact findings and
their two historical blob occurrences. All four occurrences are the same
reviewed public attribution. No new finding or scanner modification.
# Subsequent authorized stock observation and runtime correction

2026-10-10 follow-up review is in
[LIVE-READONLY-2026-10-10.md](LIVE-READONLY-2026-10-10.md).
Original PTM TX admission/ownership correction, actual-callback API-double
tests and compile/emulation runners approved as GPL-2.0-only source. Selected
stock hardware facts contain no device-private identifiers or vendor payloads.
Raw SSH logs, local connection wrapper/authentication and binaries remain
outside Git. Existing upstream attribution and scanner heuristics unchanged.
Incremental whitespace check passes; inherited 271 patch-format diagnostics and
legitimate upstream-contact findings remain explicitly reviewed, not hidden.

