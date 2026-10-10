# Local Codex Start — SBG3300-N000

1. `git clone https://github.com/gianguyen14/sbg3300-openwrt.git`; fetch and check out `handoff/sbg3300-full-openwrt-6.18.54` if published. Verify the SHA recorded in the handoff release notes before editing.
2. Read `AGENTS.md`, `STATUS.md`, `HANDOFF-HERMES.md`, `REPRODUCE.md`, `FLASH-SAFETY.md`, `docs/EVIDENCE-POLICY.md`, `docs/LOCAL-DEVELOPMENT-HANDOFF.md`, and `docs/LOCAL-DEVICE-READONLY-VALIDATION.md`.
3. Keep work on a feature branch. Save the full dirty diff before changing branch or rebasing. Do not modify `main` or force-push.
4. Use only pinned OpenWrt `5edcc1c43cb97048b506168fbbe00538956796d6` / Linux 6.18.54 for canonical builds. Rebuild only when kernel/config/toolchain inputs change; preserve verified build trees and durable logs.
5. Continue XTM from the full object-level unresolved-symbol inventory. Obtain external source only from a lawful, documented local source; review all dependency licenses. Never add a vendor mirror or uncertain derived code to the public branch. The checked-in NBuff/compat shims are probe-only and invalid as runtime implementations.
6. Establish exact SAR hardware register, descriptor, endian, DMA, IRQ, and buffer ownership semantics before writing driver code. Implement real behavior, test compile/modpost, inspect all imports. No fabricated PASS and no runtime claim from a static build.
7. Continue Ethernet/switch topology, DSL control/PHY, PCI Wi-Fi discovery, USB/GPIO, NAND/image research, package integration, and tests as offline evidence supports them. Keep guessed DSA ports and NAND partitions inactive/unapproved.
8. Hardware access: use only separately authorized, read-only checks listed in `docs/LOCAL-DEVICE-READONLY-VALIDATION.md`. Every such step remains pending until authorization. No UART, raw MTD/NAND, NVRAM/CFE writes, reset/reboot, firmware upload/flash, or experimental module loading.
9. Before commit: run tests, syntax checks, `git diff --check`, conservative secret/content and history review, and file-by-file license review. Preserve required copyright/GPL notices. Do not label a scan PASS if review findings remain.
10. Publish only reviewed, legally distributable source. Push feature branch, verify remote SHA, open a Draft PR, never merge automatically. If no write authorization, export and verify a Git bundle and patch archive with hashes/fresh import.

Current pre-final source/build evidence is in reports/PRE-FINAL-ENGINEERING.md.
Preserve the original kernel/image; the updated board disables unproved NAND
and inherited switch/MDIO activation. Do not run the full image helper until
the separate final-build approval gate is satisfied.
