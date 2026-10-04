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
