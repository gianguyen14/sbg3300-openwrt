# Source provenance

## OpenWrt

- Repository: <https://github.com/openwrt/openwrt.git>
- Pinned revision: `5edcc1c43cb97048b506168fbbe00538956796d6`
- Branch name at capture: `main` (moving name; the commit is authoritative).
- Purpose: upstream bmips/bcm63268 baseline and SBG3300 DTS/profile patch base.
- Redistribution: upstream repository license and per-component notices apply;
  this project stores its own patches, not a copy of the source tree.

## Broadcom 4.12L.06B family source

- Public mirror: <https://github.com/nomis/bcm963xx_4.12L.06B_consumer>
- Commit: `e2f23ddbb20bf75689372b6e6a5a0dc613f6e313`.
- Described family: Broadcom `100AAPP7D0_4.12L.06B_consumer_release`,
  BCM63168D0, Linux 2.6.30.
- Trust: public mirror, not an official Zyxel-hosted source archive. Use as
  `FAMILY-SOURCE`, except the exact `963168MXH_17A` boardparms entry itself,
  which is `EXACT-BOARD-SOURCE` but not proof of build identity.
- Relevant findings: boardparms and XTM implementation `bcmxtmrt` exist;
  `adsldd`, `bcmxtmcfg` implementations and PHY firmware were absent from the
  inspected source tree. The XTM source has significant vendor-kernel
  dependencies.
- Licensing: do not redistribute the full tree or proprietary firmware blobs
  until license and provenance are reviewed. It is intentionally absent from
  this public repository.

## Other public leads

Historical research included Sky SR102 BCM63168 and Actiontec T1200-family GPL
source leads, as well as `100AAJX8_4.16L.02A`. Some archive hosts were
unavailable during research. Unavailable endpoints do not prove that source
does not exist. Re-check official vendor source portals and record retrieval
date, URL, hash, and license before relying on or redistributing an artifact.

Zyxel's public GPL source request information is documented at
<https://support.zyxel.eu/hc/en-us/articles/360017067100-Zyxel-Open-Source-Code-MyZyxelPortal-How-to-Access-Zyxel-Open-Source-Code-for-Programmers-GPL>.

## Local-only evidence

Stock firmware, extracted files, stock kernel modules, physical-device dumps,
calibration data, and local release/build outputs are excluded. Reports retain
sanitized metadata, hashes where useful, and relative paths only. A hash does
not grant redistribution rights or prove that a binary can be safely used.

## Repository license note

The GitHub destination already contains an Apache-2.0 `LICENSE` file. Preserve
it during history reconciliation. OpenWrt, Linux, and kernel-oriented patch
content may carry upstream licensing and notice requirements independently;
do not assume the top-level license supersedes third-party or upstream file
licenses. Review licensing before distributing generated binaries or vendor
materials.
