# Wi-Fi port investigation

Live sysfs identifies PCI vendor/device `14e4:435f`, subsystem `14e4:0513`,
class `0x028000`; stock `wl` identifies BCM435f and reports driver family
`6.30.102.7.cpe4.12L06B.1`. Stock sysfs has no `readlink` utility, so the
read-only probe could not resolve the bound driver symlink. PCI enumeration
also shows USB `14e4:6300` and bridge `14e4:6326`.

There is a useful upstream nuance: Linux `b43_supported_bands()` maps virtual
device ID `0x435f` to “BCM6362” for band classification, but this alone does not
bind a PCI function. In the pinned kernel, `bcma_host_pci` and `b43_pci_bridge`
tables do not include `14e4:435f`; `brcmfmac` has no matching PCI entry either.
Thus no direct upstream discovery/bind path has been established for the live
PCI function. A BCM6362 virtual/SPROM path may still be relevant if the radio
is exposed through a supported BCMA/SSB host, and needs separate tracing.

The stock image contains WLAN map and NVRAM-variable files. The proprietary
`wl.ko` generic loader strings reference the corresponding variable/map path,
but this does not prove where board-specific RF calibration is stored. Do not
copy calibration, synthesize replacement data, or change NVRAM. Wi-Fi remains
`INVESTIGATING`; it is excluded from the first bring-up profile until both
driver discovery and calibration access are understood.

The 2.6.30 stock `wl.ko` is not an OpenWrt 6.18 module candidate. Its hash and
version are in `reports/STOCK-MODULE-INVENTORY.txt`.
# Wi-Fi port status

## Exact device evidence

The live PCI enumeration identified Broadcom vendor/device `14e4:435f`; the
stock `wl` driver reports BCM435f and its stock module is a big-endian MIPS32
Linux 2.6.30 module. The firmware's PCI path also enumerated an external
Broadcom 14e4:6326 PCI bridge. This confirms a PCIe-connected Broadcom WLAN
device, but not the radio revision, RF chain configuration, or calibration
layout. Device MAC and calibration contents are intentionally excluded.

The extracted stock `wl.ko` SHA256 is recorded in
`reports/STOCK-MODULE-INVENTORY.txt`; it is proprietary and is not a candidate
for a 6.18 OpenWrt kernel. Matching ABI/loader compatibility is not plausible
without a vendor port and module rebuild.

## Upstream driver check

The Linux Wireless brcm80211 documentation lists PCIe BCM4350 as device
`14e4:43a3`; it does not list the observed `14e4:435f`. In the pinned OpenWrt
checkout, the upstream brcmfmac PCI device table also has no `0x435f` match.
The OpenWrt Sky SR102 device page separately identifies `BCM435F` / `14e4:435f`
as an SoC-integrated pseudo-ID and says there is no usable driver. This is a
close BCM63168-family comparison, not a proof of SBG3300 board internals; it
does make an ordinary brcmfmac/brcmsmac PCI device port unlikely.

The matching 4.12L.06B source tree has no Broadcom `wl` host-driver source. It
does contain legacy WLAN map/configuration blobs, and the exact stock `wl.ko`
contains a generic loader path for `/etc/wlan/bcm%04x_nvramvars.bin`; no blob
contents or calibration data are copied into the port. The stock driver binary
is tied to Linux 2.6.30 and is not a viable 6.18 driver artifact.

## Strategy and gate

Current decision: `UNSUPPORTED` for the initial OpenWrt port, with a vendor
source search still open. Keep Wi-Fi out of first board bring-up. Reconsider
only if a rebuildable host driver matching this pseudo-device is recovered.
No calibration or NVRAM data will be copied into the project. A binary `.ko`
from the 2.6.30 stock kernel will not be loaded into OpenWrt.

Sources checked:

- Pinned OpenWrt checkout `5edcc1c43cb97048b506168fbbe00538956796d6`;
- [Linux Wireless brcm80211 driver documentation](https://wireless.docs.kernel.org/en/latest/en/users/drivers/brcm80211.html);
- [OpenWrt Sky SR102 device record](https://openwrt.org/toh/sky/sr102) (same SoC family; comparison evidence only).
