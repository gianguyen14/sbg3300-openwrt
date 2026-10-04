# Instructions for coding agents

1. Read `STATUS.md`, `HANDOFF-HERMES.md`, and `FLASH-SAFETY.md` before
   changing code or making hardware claims.
2. This is an offline research port. Do not access, configure, reboot, upload to,
   or flash the owner's router unless a later task explicitly authorizes a
   specific safe device test. No UART, raw NAND/MTD operation, factory reset,
   or destructive NVRAM operation is allowed.
3. Never put passwords, PPP/Wi-Fi credentials, tokens, private keys, cookies,
   MAC addresses, serials, calibration, NVRAM, firmware, extracted proprietary
   trees, or unlicensed vendor blobs in Git.
4. Preserve the evidence labels and confidence boundaries in
   `docs/EVIDENCE-POLICY.md`. A successful compile is not a boot, runtime,
   link, DSL sync, or recovery result.
5. Do not copy sibling-board topology into SBG3300 DTS without independent
   evidence. Keep unknown hardware disabled or explicitly unresolved.
6. Make incremental, reviewable patches. Preserve failed compile probes and
   negative findings; correct their interpretation, do not erase them.
7. Before committing: run relevant tests, `git diff --check`, shell/Python
   syntax checks, and a local secret/proprietary-material scan. Never upload
   repository contents to an external scanning service.
8. Update `STATUS.md`, handoff state, and relevant reports after meaningful
   work. State exact source revisions and artifact hashes where applicable.
9. The only current SBG3300 image artifact is a research initramfs ELF that is
   `OFFLINE-ONLY` and `NOT-FLASHABLE`. Do not create or label a factory or
   sysupgrade image without satisfying the safety gates and obtaining explicit
   authorization for any later device action.
