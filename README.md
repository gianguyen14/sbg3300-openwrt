# Zyxel SBG3300-N000 OpenWrt Full Port

Status: **PARTIAL-PORT / OFFLINE-ONLY / NOT-FLASHABLE**

This repository is the shared source of truth for the Zyxel SBG3300-N000 OpenWrt port so that Codex, Hermes, or another engineer can continue the work even when they are not physically near the modem/router.

## Current goal

Port current OpenWrt `bmips/bcm63268` to the Zyxel SBG3300-N000 while keeping a strict fail-closed policy:

- BCM63168D0 / BMIPS4350
- 128 MiB RAM
- 128 MiB NAND
- Ethernet + external Broadcom switch
- USB
- DSL/XTM
- PPP over DSL
- Wi-Fi if technically viable
- no legacy Zyxel management attack surface in the final full-OpenWrt branch

## Safety status

**Do not flash any artifact from this repository yet.**

The current SBG3300 artifact is an offline initramfs research build only. It is not a factory image, not a sysupgrade image, and has not been runtime-boot validated on hardware.

Absolute project rules:

- no UART dependency
- no raw MTD writes
- no `dd` to MTD
- no `nandwrite`
- no `flash_erase`
- no bootloader/CFE modification
- no factory reset
- no PPP credential changes
- no MAC/NVRAM/calibration changes
- no router firmware upload unless the owner explicitly authorizes it after all gates pass
- do not publish secrets, PPP identity, device-unique keys, MAC addresses, serials, tokens, or calibration dumps

## Current proven milestones

- clean current OpenWrt upstream baseline for `bmips/bcm63268` builds successfully
- SBG3300 Kconfig/profile builds successfully
- SBG3300 DTS compiles
- SBG3300 initramfs loader ELF is produced successfully
- reproducible build flow exists
- release R&D bundle/checksums have been validated locally
- XTM source has been compile-probed against Linux/OpenWrt 6.18
- exact stock DSL modules have been inventoried
- live hardware evidence has been collected read-only from the router

See **HERMES-HANDOFF.md** for the full technical state, evidence levels, blockers, and next work items.

## Current classification

```text
Project                    PARTIAL-PORT
Upstream bmips baseline    PASS
SBG3300 profile build      PASS
SBG3300 DTS build          PASS
SBG3300 initramfs build    PASS (offline only)
Runtime boot               NOT TESTED
NAND flash safety          PARTIAL
Ethernet/switch topology   PARTIAL
DSL/XTM                    ACTIVE PORTING
Wi-Fi                      INVESTIGATING / DEFERRED
Factory image              NOT CREATED
Sysupgrade                 NOT CREATED
Recovery path              UNPROVEN
Flash authorization        NO
```

## Remote-worker rule

If you are Hermes or another worker without physical access to the modem:

1. Treat GitHub as the source of truth.
2. Continue only offline-safe work: source research, static analysis, build, DTS review, kernel/API porting, image parsing, tests, and documentation.
3. Never claim runtime PASS without evidence from the physical router.
4. Never ask to flash just to test a theory.
5. Commit every material discovery and update the handoff/status docs so the next worker can continue without the modem.
