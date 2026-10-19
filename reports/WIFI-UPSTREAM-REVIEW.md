# BCM435f / BCM6362 upstream discovery review

Date: 2026-10-04

## Live device

Read-only sysfs inspection returned one WLAN-class PCI function:

| Field | Value |
|---|---|
| PCI address | `0000:00:00.0` |
| Vendor/device | `14e4:435f` |
| Subsystem | `14e4:0513` |
| Class | `0x028000` |
| Stock driver | proprietary `wl`, `6.30.102.7.cpe4.12L06B.1` |

The same enumeration found two `14e4:6300` USB host functions and bridge
`14e4:6326`. The stock environment lacks `readlink`, so driver symlink and
parent resolution could not be established by that probe. No MAC or calibration
data was collected.

## Pinned Linux/OpenWrt source evidence

OpenWrt commit `5edcc1c43cb97048b506168fbbe00538956796d6` builds Linux
6.18.54. In its `drivers/net/wireless/broadcom/b43/main.c`,
`b43_supported_bands()` has `case 0x435f: /* BCM6362 */`. The helper first
obtains a bus device ID and may override it from SPROM; this is a supported-band
classification after b43 has already discovered a core. It is **not** a PCI ID
probe/bind table.

The same pinned tree's direct discovery lists were checked:

- `drivers/bcma/host_pci.c`: PCI bridge table does not list `14e4:435f`.
- `drivers/ssb/b43_pci_bridge.c`: b43 SSB bridge table does not list
  `14e4:435f`.
- `drivers/net/wireless/broadcom/brcm80211/brcmfmac/pcie.c`: no `0x435f`
  match.

This means the existing b43 comment alone does not demonstrate that the live
PCI function can bind through the stock OpenWrt discovery path. It leaves an
investigation lead: determine whether the WLAN core is reachable through a
separate BCMA/SSB host or is instead a direct PCI function requiring new host
glue. No glue patch was attempted because the bus mapping and calibration
source are not yet proven.

## Calibration and distribution

The extracted stock rootfs has WLAN map and NVRAM-variable files, and stock
`wl.ko` contains generic paths that load device-specific data. These strings
do not establish whether RF calibration lives in file data, ROM, NVRAM, or a
combination. Do not generate, patch, or distribute a replacement calibration
blob. The 2.6.30 `wl.ko` is incompatible with the 6.18 kernel ABI and is not
used in the offline image.

## Status

`INVESTIGATING`; no Wi-Fi support is included in the initial profile. No radio
runtime test was performed under OpenWrt. An eventual driver build or PCI bind
would still not prove correct RF calibration or regulatory behavior.

## Authorized stock/source cross-check, 2026-10-10

`LIVE-DEVICE`: PCI sysfs driver symlink now confirms `wl` and IRQ 15.
Boot explicitly reports SROM/OTP not programmed, memory-mapped SROM data and
loading the WLAN map/common-variable files. Those private files were not read;
upstream calibration format and legal provision remain unresolved.

`FAMILY-SOURCE`, mirror revision
`e2f23ddbb20bf75689372b6e6a5a0dc613f6e313`:

- `bcmdrivers/opensource/include/bcm963xx/bcmpci.h:31-34` defines on-chip
  WLAN slot 0, packed ID `0x435f14e4` and resource size `0x2000`.
- `kernel/linux/arch/mips/pci/ops-bcm63xx.c:57-79` supplies a software PCI
  configuration header for CONFIG_BCM963268, including class `0x028000` and
  subsystem `0x051314e4`; its read/write handlers at 370/405 access that array.
  This is a synthetic PCI presentation of on-chip WLAN in that source.
- `shared/opensource/include/bcm963xx/63268_map_part.h:50` gives family
  WLAN ChipCommon physical base `0x10004000`.

`INFERENCE`: the observed ID/slot/subsystem are consistent with this virtual
PCI lineage; enumeration is not proof of a discrete PCIe radio or justification
for simply adding a PCI ID to b43/BCMA. Live BAR0 is `0xa0000000` (64 KiB),
different from the family ChipCommon resource. The running Zyxel mapping/fixup,
AI/EROM cores and MMIO/endian/DMA/IRQ translations are still unproven.

`UPSTREAM`: Linux 6.18.54 `drivers/bcma/host_soc.c` has an OF `brcm,bus-axi`
host using of_iomap, bus enumeration and DT core interrupts. Kconfig's help
limits established SoC support to BCM47xx; that does not prove BCM63168
compatibility. The earlier preflight built only the PCI host. The additional
SoC-host configuration is **offline compile coverage only**, with BCMA serial
flash disabled. No SBG3300 BCMA node, PCI ID workaround or calibration blob is
enabled. Build results are recorded in LIVE-READONLY-2026-10-10.md.

The pinned OpenWrt-prepared kernel also carries GPL fallback-SPROM support in
`drivers/bcma/fallback-sprom.c`. Its `bcma_get_fallback_sprom()` explicitly
rejects non-PCI hosts with `-ENOENT`. Thus compiling `host_soc` does not provide
a SoC calibration path. `bcma_arch_register_fallback_sprom()` exists but is
not exported for an external provider module. A future verified host needs a
legal calibration provider/matching contract in addition to MMIO/core discovery;
no such provider is installed here. Existing PCI firmware-loading support is
not evidence that the stock map file can be used unchanged.

## Non-DSL AP software build, 2026-10-11

The pinned synthetic-PCI source was checked byte-for-byte against the public
mirror revision. `fixup-bcm63xx.c:105–108` also resets the synthetic WLAN BAR
resource to the family ChipCommon base; it does not explain the running stock
BAR discrepancy or provide an upstream host registration contract. No raw BAR,
EROM, SPROM or calibration was read. Existing SoC/PCI BCMA, SSB, b43 and
brcmfmac compile coverage remains valid; their discovery/firmware/calibration
blockers are unchanged. Do not inject 435f into a PCI table.

An isolated copy of the verified OpenWrt package environment now selects and
actually builds `wpad-basic-openssl`. Target compile exits 0, zero compiler
warnings/errors, with CONFIG_DRIVER_NL80211=y and 802.11n/ac user-space support.
AP package: 564122 bytes, SHA256
`221e5dfe32b0a5607596d4ccb9b18bf67effcfa0f7847cbcb1b9a1b4a62d598c`.
Installed multicall executable: 1286420 bytes, ELF32 MIPS BE/o32 PIE; SHA256
`bdb61892f04746adb9f75140a36fee54ebd07c6bbe9c993aa9af9fe97f6ced5d`.
It is a software artifact, not an onboard-radio binding or AP association test.

MIPS QEMU version-only invocations execute the actual target program with the
private staged target root's dynamic libraries. hostapd v2.12 prints its version
and exits 1, exactly its main.c:930–934 convention. wpa_supplicant v2.12 exits 0.
No interfaces or RF hardware are accessed. The first QEMU prefix pointed at the
staging directory rather than root-bmips and failed to find the interpreter
(exit 255); the corrected root resolves it. The initial package-selection
invocation mistakenly treated scripts/config (a directory) as an executable;
that unselected/no-artifact run is not counted. Corrected selection plus actual
artifact existence establishes the build. Defconfig retains the previously
known unrelated qt5base/squeezelite feed recursion diagnostics; target package
C compilation itself has none. All logs and artifacts remain private.

`configs/sbg3300-pre-final.config` includes this optional package for compile
coverage. It is not a production WLAN configuration and provides no firmware,
calibration, regulatory overrides or guessed radio node. Existing routing,
firewall/DHCP package builds remain separate from physical Ethernet evidence.

Alternative future use of a supported external USB radio still requires an
actual dongle VID/PID, its driver and lawful firmware, USB VBUS/runtime evidence
and AP testing. An external Ethernet access point can avoid onboard-radio
binding once Ethernet works; neither alternative proves internal Wi-Fi support.
