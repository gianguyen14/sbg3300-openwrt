# Local Development Handoff — Zyxel SBG3300-N000

## State at handoff

This repository is offline research and OpenWrt port work. The device was not accessed by the remote agent. No generated image is authorized for installation. Never use UART, raw MTD, NAND writes, CFE/NVRAM changes, reset/reboot, firmware upload/flash, or experimental module loading.

The pinned OpenWrt revision is `5edcc1c43cb97048b506168fbbe00538956796d6`, target `bmips/bcm63268`, kernel `6.18.54`. A successful static `target/linux/compile` completed in `/home/hermes/sbg3300-build/openwrt`; evidence and hashes are in `reports/XTM-DURABLE-BUILD-EVIDENCE.md` when available in this checkout and in `reports/LOCAL-HANDOFF-STATE.yaml`. Kernel success is not XTM success or hardware validation.

XTM status: source port is not a runtime candidate; canonical external Kbuild reaches modpost only with diagnostic/probe shims and fails with 19 unique unresolved imports derived by comparing object `nm -u` against module-local definitions and the pinned `Module.symvers`. The checked-in inventory is `reports/XTM-UNRESOLVED-CANONICAL-6.18.54.tsv`. No XTM `.ko` exists. Vendor sources are local external dependencies and must not be copied/published without file-by-file license review.

## Hardware identity and evidence boundary

Research evidence identifies Zyxel SBG3300-N000, board `963168MXH_17A`, BCM63168D0 family. Hardware runtime behavior remains unvalidated. Consult `docs/EVIDENCE-POLICY.md`, `STATUS.md`, and `FLASH-SAFETY.md` before claims or device work. Do not enable speculative DTS nodes or guessed partitions.

## Repository map

- `patches/openwrt/`: the conservative offline SBG3300 profile patches. This public handoff does not contain `patches/dsl/`, `patches/switch/`, or XTM implementation patches.
- `dts/`, `configs/`: offline device profile and build configurations; not flash approval.
- `compat/`: absent from this public handoff checkout. Do not assume the private probe shims described in earlier research are available here or use them in a runtime candidate.
- `reports/`: evidence and blocker records. The durable build log, XTM compile log, and noncanonical probe logs were not transferred in this checkout; hashes and summarized evidence are retained where available.
- `tests/`, `tools/`: offline tests and build/research helpers.
- `source/vendor/README.md`: source lineage metadata only. External vendor trees remain outside Git.

## Pinned build reproduction

Use `docs/LOCAL-BUILD-QUICKSTART.md`. Prefer a persistent checkout outside `/tmp`; verify the exact commit, `.54` declaration, target configuration, and complete build inputs. Preserve complete logs and real exit codes. Do not treat output artifacts from another commit/kernel/config as valid.

## XTM source and dependencies

Historical source work was recorded outside this public handoff; the referenced research commit is not present in this checkout. A separately available, Git-ignored mirror is identified in `source/vendor/README.md`. Its main driver files carry Broadcom DUAL/GPL notices referencing GPL-2.0, but that does not establish rights for every included implementation, header, binary, or dependency. The historical Makefile hardcoded local include paths and enabled BLOG. Review each file and dependency before reuse or redistribution; keep the mirror and any derived changes outside public Git until that review is complete.

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
