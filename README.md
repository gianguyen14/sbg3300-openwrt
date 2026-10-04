# Zyxel SBG3300-N000 OpenWrt Port

> ⚠️ **RESEARCH / PARTIAL PORT**
>
> ⚠️ **OFFLINE ONLY — NOT FLASHABLE**
>
> ⚠️ **NO OPENWRT RUNTIME VALIDATION ON THE ROUTER**

There is currently **no approved flashable SBG3300 image**. The profile builds
an initramfs ELF for offline analysis. Build success does not imply that CFE
can load it, that the board boots, or that any peripheral works.

This project aims for a full OpenWrt port while preserving the existing
stock-custom router as an independent reference and recovery system. The target
is a Zyxel SBG3300-N000, board `963168MXH_17A`, Broadcom BCM63168D0, on the
upstream `bmips/bcm63268` target.

## Current state

- Overall: **PARTIAL-PORT**.
- Pinned OpenWrt source: `5edcc1c43cb97048b506168fbbe00538956796d6`.
- Linux kernel in the recorded build: `6.18.54`.
- Unmodified bmips baseline and the SBG3300 offline initramfs profile both
  built successfully on the original build host.
- The SBG3300 DTS compiles and round-trips. It deliberately omits speculative
  partitions, switch topology, GPIOs, and console requirements.
- Exact Ethernet/DSA wiring and NAND writer semantics remain unresolved.
- The Broadcom XTM source has been compile-probed against 6.18 and has real
  compatibility failures. The ADSL and XTM-configuration implementations are
  absent from the inspected public source mirror. DSL sync is untested.
- Wi-Fi PCI identity is known, but OpenWrt discovery/binding and calibration
  access are unproven.

See [STATUS.md](STATUS.md) for the evidence matrix and
[HANDOFF-HERMES.md](HANDOFF-HERMES.md) for the remote continuation brief.

## Hardware and subsystem notes

- [HARDWARE.md](HARDWARE.md): observed device facts and evidence provenance.
- [NAND-MAP.md](NAND-MAP.md): physical extents, dual-slot corroboration, and
  unresolved writer/bad-block behavior.
- [SWITCH-PORT.md](SWITCH-PORT.md): boardparms/HSSPI evidence and unknown
  physical port mapping.
- [DSL-PORT.md](DSL-PORT.md): stock modules, vendor XTM source, compile probe,
  and missing components.
- [WIFI-PORT.md](WIFI-PORT.md): PCI identity and limits of the b43 evidence.
- [FLASH-SAFETY.md](FLASH-SAFETY.md): hard stop conditions.

## Reproduce

Start with [REPRODUCE.md](REPRODUCE.md). It uses the pinned upstream commit and
the checked-in patch series; no workstation-specific checkout is required.
Generated images, downloaded source trees, stock firmware, vendor trees, and
device-specific data are not in this repository.

## Safety

Do not flash any artifact from this project. There is no SBG3300 factory image,
sysupgrade image, validated boot handoff, proven recovery route, or runtime
test. Do not use raw NAND operations. The currently working stock-custom router
is kept separate and must remain untouched during offline port work.

## Contributing

Read [AGENTS.md](AGENTS.md), preserve the evidence labels in
[docs/EVIDENCE-POLICY.md](docs/EVIDENCE-POLICY.md), and update `STATUS.md` after
meaningful findings. A compile result is a build result, never a hardware
runtime result. Vendor blobs and extracted firmware are excluded unless their
redistribution rights are established.
