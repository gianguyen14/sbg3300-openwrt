# SBG3300 non-DSL engineering milestone

Date: 2026-10-10

Scope: pinned OpenWrt `5edcc1c43cb97048b506168fbbe00538956796d6`, Linux
6.18.54, `bmips/bcm63268`. DSL is deferred. No final firmware image was built.

## Work branch and preservation

The working branch `feat/sbg3300-nondsl-ethernet-wifi` starts at the reviewed
integration commit `ee212d7a8920cd7b264693dbc02c86e8a483f7c0`. The existing
OpenWrt source checkout, vendor mirrors, build directories and prior artifacts
were left intact. XTM/PTM implementation, tests, reports and build results are
preserved and unchanged.

## Read-only stock evidence

The owner's existing `sbg3300` command resolved to a local executable wrapper.
Its saved host key was already present; the connection used the existing
authentication setup. Only read-only sysfs metadata was queried. No MAC,
serial, calibration, credential, register contents or flash data were read.

- `LIVE-DEVICE`: `/sys/bus/spi/devices/spi1.0` reports modalias and bound driver
  `bcm_HSSpiDev0`. This identifies the stock HS-SPI child as the generic driver
  only; it does not identify a switch chip, chip-select wiring or CPU port.
- `LIVE-DEVICE`: Ethernet-class logical netdevices expose carrier states, but
  their sysfs device-driver links do not establish a physical jack map. The
  previously recorded stock mapping to switch indices remains logical-port
  evidence only.
- `LIVE-DEVICE`: PCI `14e4:435f` remains bound to stock `wl`; PCI `14e4:6300`
  host functions remain bound to OHCI and EHCI. This does not establish an
  upstream Linux 6.18 Wi-Fi binding or USB peripheral operation.
- No switch-control, selector, register, module, or vendor diagnostic command
  was run. Device state was not changed.

The dated read-only source report remains
[`LIVE-READONLY-2026-10-10.md`](LIVE-READONLY-2026-10-10.md).

## Ethernet and switch boundary

`BUILD-RESULT`: the pinned Linux kernel already compiles `bcm6368-enetsw`,
`b53_spi`, DSA core and Broadcom DSA tags in the isolated pre-final
configuration. The strict external `bcm6368-enetsw` artifact is ELF32 MIPS
big-endian/o32 with vermagic `6.18.54 SMP mod_unload BMIPS 32BIT`, 85 imports
and zero missing imports; SHA256 is
`89c26b4d872fb86a9f8839bbbe9f077ce64e5f7f99017d9258ccf1bd54e8f1b2`.
The expanded-kernel B53 SPI module is also recorded in
`PRE-FINAL-ACCEPTED-ARTIFACTS.tsv`. These are compile results only.

Native, Clang ASan/UBSan and static MIPS user-mode tests cover Ethernet IRQ
error/defer/optional-absence handling and DMA channel resource bounds. The
existing driver patch adds managed clock/reset/PM/NAPI/netdev lifetime cleanup
and is included in the compiled kernel candidate. No test proves Ethernet
traffic or switch behavior.

`EXACT-BOARD-SOURCE` remains ambiguous between board variants: the board entry
contains both memory-mapped and HS-SPI switch groups, including a comment about
an alternate chip-select/MDIO resistor configuration. `LIVE-DEVICE` confirms
only generic `spi1.0` binding. Exact switch ID, active chip-select, CPU-facing
interface, RGMII delays, PHY addresses/reset wiring, MAC selection, WAN/LAN
separation and physical jack numbering remain `UNKNOWN`. Therefore the SBG3300
switch/MDIO topology stays disabled, and no WAN/LAN UCI mapping is supplied.

### B53 SPI package feasibility check

`UPSTREAM`: the pinned `target/linux/bmips/bcm63268/config-6.18` sets
`CONFIG_NET_DSA=y`, `CONFIG_B53=y`, `CONFIG_B53_SPI_DRIVER=y` and
`CONFIG_BCM6368_ENETSW=y`. In this target profile these are built into the
kernel; the `b53_spi.ko` listed in the accepted artifact inventory came from a
separate compile-coverage configuration where that frontend was modular. The
existing OpenWrt `kmod-dsa-b53` recipe packages B53 common/tag support but does
not package `b53_spi.ko`.

An isolated package feasibility probe selected a temporary `kmod-dsa-b53-spi`
candidate and its dependencies. `make defconfig` exited 0 but emitted recursive
Kconfig dependency diagnostics for unrelated `qt5base-gui` and
`squeezelite-custom` feed options, as well as missing optional feed-package
warnings. The resulting bcm63268 kernel config kept `B53_SPI_DRIVER=y`, and the
expected `b53_spi.ko` did not exist. No package compile was run and no package
artifact was produced. The candidate package patch was not retained in the
public patch series; the probe itself remains in the isolated scratch build
tree. Changing this SoC-wide built-in selection to a module would alter
behavior for every board in the subtarget and is not justified by the
unresolved SBG3300 switch identity/topology. No target config file or original
source checkout was changed. The package option existed only in the isolated
scratch copy's ignored `.config`.

## Wi-Fi, boot, storage and peripherals

- `UPSTREAM` and `BUILD-RESULT`: b43, brcmfmac, BCMA and SSB components compile.
  The pinned driver discovery tables do not bind the observed PCI ID directly.
  Exact-family source presents an on-chip WLAN function through synthetic PCI
  configuration, but its MMIO mapping differs from the live BAR observation;
  SoC-host discovery and legal calibration provisioning remain unresolved.
  Do not add a PCI-ID workaround, calibration, firmware or regulatory values.
- `LIVE-DEVICE`: NAND metadata gives page/OOB/erase geometry without raw reads.
  Modern ECC/OOB parameters, exact writer/BBT translation, CFE handoff and a
  non-UART recovery path remain unresolved. NAND nodes and partitions stay
  disabled.
- `BUILD-RESULT`: exact-SoC USB PHY and EHCI/OHCI, GPIO/pinctrl, LED, button and
  watchdog drivers have compile coverage. Board wiring, polarity, VBUS and
  OpenWrt runtime behavior are unverified; no board controls are enabled.
- Existing initramfs loader artifact remains
  `OFFLINE-ONLY` / `NOT-FLASHABLE`, SHA256
  `3961a39d5d554ce467b9575bbc6f6293d385ddda9fc4dc9b3dbf0c3cf8027b51`.
  Its strict static loader audit remains unresolved; it is not evidence of CFE
  acceptance. No final/factory/sysupgrade image was built.

## Tests repeated for this milestone

- `python3 -m unittest discover -s tests -q`: 19 tests passed.
- `bash tools/test-enetsw-contract.sh`: passed.
- Clang ASan/UBSan Ethernet contract test: passed.
- `bash tools/test-contracts-mips.sh`: XTM regression suite, PTM policy,
  Ethernet contracts and TX callback tests passed under MIPS user-mode QEMU.
- `bash -n tools/*.sh` and `python3 -m compileall -q tools tests`: passed.
- B53 SPI package feasibility: `BLOCKED`; no package build result is claimed.

Previously completed kernel/package/DTS builds are preserved and listed in
`PRE-FINAL-ENGINEERING.md`, `PRE-FINAL-ACCEPTED-ARTIFACTS.tsv` and
`PRE-FINAL-PACKAGES.tsv`; they were not repeated because their inputs are
unchanged. No final full firmware image build was started.

## Status and next evidence needed

| Area | Status | Evidence needed for a later step |
|---|---|---|
| Ethernet MAC/DMA | `COMPILED`; hardware `NOT-TESTED` | OpenWrt runtime boot, interface ownership, traffic and teardown evidence |
| External switch / WAN-LAN | `BLOCKED` | Non-invasive exact switch identification and board wiring/CPU port/PHY/MAC topology evidence |
| Wi-Fi | `BLOCKED` | Verified host/core mapping plus lawful calibration and firmware interface |
| NAND/boot | `BLOCKED` | Exact ECC/writer/BBT/container semantics, CFE loader requirements and safe recovery proof |
| USB/peripherals | `COMPILED`; wiring/runtime `UNKNOWN` | Exact board pin/power wiring and OpenWrt runtime validation |
| DSL | `DEFERRED — NOT PART OF CURRENT MILESTONE` | Resume only when owner requests it |

The current evidence does not justify an Ethernet-only Full OpenWrt image: the
switch topology and WAN/LAN mapping are unresolved, and the existing initramfs
ELF has not passed a CFE compatibility audit. Do not build a final firmware
image, boot it, or install it without the separate approval gate.

No public-source license issue was introduced in this milestone; the report
contains source-level facts and non-identifying read-only observations only.
Local publication scanner and whitespace checks are recorded with the branch
review before push.
