# Wi-Fi port investigation

Live sysfs identifies PCI vendor/device `14e4:435f`; stock `wl` identifies
BCM435f and reports driver family `6.30.102.7.cpe4.12L06B.1`. The stock image
contains WLAN map and NVRAM-variable files. This is not sufficient to establish
upstream driver support or the calibration source/offset.

Next steps: map PCIe topology, correlate the chip/revision with upstream
`b43`/`brcmfmac` support tables, inspect firmware requirements, and identify
where board-specific calibration is stored without exporting its contents.
Do not synthesize or overwrite calibration data. Until then Wi-Fi status is
`INVESTIGATING`, not supported.
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
Therefore a mainline driver is not established for this exact PCI ID. This
does not prove the chip cannot share code with another family; a full revision
and firmware/NVRAM compatibility check would be required before attempting
quirks or adding an ID.

## Strategy and gate

Current decision: `VENDOR-PORT OR UNSUPPORTED`, not `MAINLINE`. Keep Wi-Fi out
of the first board bring-up. Next evidence needed is the stock `wl` chip/rev
report, `wl` firmware/NVRAM load path, radio calibration storage location and
whether any vendor GPL tree contains rebuildable driver sources. No calibration
or NVRAM data will be copied into the project. A binary `.ko` from the 2.6.30
stock kernel will not be loaded into OpenWrt.

Sources checked:

- Pinned OpenWrt checkout `5edcc1c43cb97048b506168fbbe00538956796d6`;
- [Linux Wireless brcm80211 driver documentation](https://wireless.docs.kernel.org/en/latest/en/users/drivers/brcm80211.html).
