# License and Redistribution Review — Proposed Handoff Branch

Reviewed only selected clean-main files and newly added handoff materials. This is a preliminary review, not blanket approval for all reachable historical content.

- New handoff documents, YAML status, and symbol inventory are original project documentation/data and contain no vendor implementation source.
- OpenWrt patch files retain SPDX/license notices from upstream or project patch headers; preserve original attribution. Their exact target-file upstream licenses remain GPL-compatible and are not relicensed by the repository Apache license.
- Existing upstream-derived DTS/patches must retain source copyright/license terms.
- XTM compatibility/DMA files and historical vendor-derived source are not included in this branch due unresolved provenance and safety issues.
- External Broadcom XTM and DSL source/headers are excluded; no license for every dependency has been established. The Broadcom DUAL/GPL header on selected historical C files alone is insufficient.
- The public scanner found reachable historical email placeholders and MAC-like vendor source examples. They require human review; scanner result is REVIEW REQUIRED. Do not publish branch until authorized reviewer accepts or removes/sanitizes them while preserving valid attribution.
- No stock firmware, binary driver, DSL firmware, NVRAM, calibration, credentials, private key, or device dump was intentionally added.

Status: LICENSE REVIEW INCOMPLETE; PUBLICATION BLOCKED pending review of reachable history findings and patch/source provenance.
