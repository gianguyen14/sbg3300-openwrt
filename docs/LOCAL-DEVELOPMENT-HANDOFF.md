# Local Development Handoff — Zyxel SBG3300-N000

## State at handoff

This repository is offline research and OpenWrt port work. The device was not accessed by the remote agent. No generated image is authorized for installation. Never use UART, raw MTD, NAND writes, CFE/NVRAM changes, reset/reboot, firmware upload/flash, or experimental module loading.

The pinned OpenWrt revision is `5edcc1c43cb97048b506168fbbe00538956796d6`, target `bmips/bcm63268`, kernel `6.18.54`. A successful static `target/linux/compile` completed in `/home/hermes/sbg3300-build/openwrt`; evidence and hashes are in `reports/XTM-DURABLE-BUILD-EVIDENCE.md` when available in this checkout and in `reports/LOCAL-HANDOFF-STATE.yaml`. Kernel success is not XTM success or hardware validation.

XTM status: source port is not a runtime candidate; canonical external Kbuild reaches modpost only with diagnostic/probe shims and fails with 19 unique unresolved imports derived by comparing object `nm -u` against module-local definitions and the pinned `Module.symvers`. The checked-in inventory is `reports/XTM-UNRESOLVED-CANONICAL-6.18.54.tsv`. No XTM `.ko` exists. Vendor sources are local external dependencies and must not be copied/published without file-by-file license review.

## Hardware identity and evidence boundary

Research evidence identifies Zyxel SBG3300-N000, board `963168MXH_17A`, BCM63168D0 family. Hardware runtime behavior remains unvalidated. Consult `docs/EVIDENCE-POLICY.md`, `STATUS.md`, and `FLASH-SAFETY.md` before claims or device work. Do not enable speculative DTS nodes or guessed partitions.

## Repository map

- `patches/openwrt/`, `patches/dsl/`, `patches/switch/`: upstream/RFC patches; RFC-only material must remain inactive.
- `dts/`, `configs/`: offline device profile and build configurations; not flash approval.
- `compat/`: XTM DMA research and compatibility/probe code. `compat/linux/nbuff.h` and `compat/xtm_compat.h` contain fake semantics and are PROBE-ONLY; never include in runtime-candidate builds.
- `reports/`: evidence and blocker records. `reports/logs/xtm-probe-noncanonical-6.18.52.log` is historical and noncanonical.
- `tests/`, `tools/`: offline tests and build/research helpers.
- `source/vendor/README.md`: source lineage metadata only. External vendor trees remain outside Git.

## Pinned build reproduction

Use `docs/LOCAL-BUILD-QUICKSTART.md`. Prefer a persistent checkout outside `/tmp`; verify the exact commit, `.54` declaration, target configuration, and complete build inputs. Preserve complete logs and real exit codes. Do not treat output artifacts from another commit/kernel/config as valid.

## XTM source and dependencies

Historical source was recorded in commit `4915412012bf93ce52e6671531dd968da1da573f`. Its main driver files contain Broadcom DUAL/GPL notices referencing GPL-2.0, but that does not establish rights for every included implementation, header, binary, or dependency. The historical Makefile hardcoded local include paths and enabled BLOG. The local external mirror is identified in `source/vendor/README.md`; obtain its contents from a lawful local source and review each file before reuse or redistribution.

XTM next steps: review all canonical probe diagnostics, use the exact pinned kernel and public Linux APIs, establish register/descriptor semantics from lawful sources, then replace one real dependency at a time. Do not force FKB false, add empty helpers, or use fake IRQ/DMA/cache success. The public unresolved-symbol table is a measurement, not evidence that the functions are irreducible.

## Subsystem status

- BCM63168 XTM: canonical kernel built; XTM C probe progressed but modpost fails. No module/runtime pass.
- Ethernet/internal MAC: partial research only; do not infer exact port behavior without evidence.
- BCM53125: strong candidate / runtime-unproven; topology RFC inactive.
- DSL control (`bcmxtmcfg`): unresolved, ABI research only.
- DSL PHY (`adsldd`) and firmware: unresolved; no proprietary firmware redistribution.
- Wi-Fi PCI 14e4:435f: discovery and driver binding unproven.
- USB/LED/GPIO: partial candidate research; runtime untested.
- NAND/image writer: research only; fixed partitions not approved; no physical MTD operations.
- Full OpenWrt integrated build and router runtime: not validated.

## Legal/publication rules

Preserve upstream and GPL notices. Apache-2.0 project licensing does not relicense GPL/vendor files. Keep proprietary/uncertain external source, stock firmware, binary blobs, calibration, NVRAM, credentials, private keys, device dumps, MAC/serial identifiers and local build products out of public Git. Run a conservative content/history audit and manually review every finding before publication.

## Hardware boundary

A separately authorized local operator may later run the pending, read-only checklist in `docs/LOCAL-DEVICE-READONLY-VALIDATION.md`. This document does not authorize execution. Never flash, reboot, reset, configure, read raw flash, or load experimental code.
