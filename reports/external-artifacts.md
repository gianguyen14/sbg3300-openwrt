# External source artifacts

Hashes below are SHA256 of a deterministic uncompressed `git archive` of the
recorded commit. They fingerprint tracked source at that commit; they are not
hashes of repository metadata or untracked/local files.

| Artifact | URL | Retrieved | Revision | Archive SHA256 | Trust / license |
|---|---|---|---|---|---|
| OpenWrt | `https://github.com/openwrt/openwrt.git` | 2026-10-04 | `5edcc1c43cb97048b506168fbbe00538956796d6` (`main`) | `c7aaab7ff18de097fbfdc304763e2c9c25a564486932b3a8b08302b8076891a0` | Official upstream; OpenWrt project licensing applies |
| BCM963xx 4.12L.06B consumer source mirror | `https://github.com/nomis/bcm963xx_4.12L.06B_consumer.git` | 2026-10-04 | `e2f23ddbb20bf75689372b6e6a5a0dc613f6e313` | `6c1c585a44887ffcb824857ba2171cc8376139adfb79da7e6e220e629d272181` | Secondary public mirror; source tree's redistribution/licensing terms are not yet audited. Keep local-only; do not redistribute proprietary objects/blobs. |
| Broadcom GPL driver comparison tree | `https://github.com/jclehner/bcmdrivers-gpl-bcm963xx.git` | 2026-10-04 | `1555117dd9e5b393cf5b92e10e603e1c5f8ba2bb` | `119904b6d458577bd9a45dec262423a527a020314c816b8f06099e4a6724c511` | Secondary mirror, later/non-matching SoC lineage; useful XTM comparison only, no ADSL or XTM-config driver sources. Local-only pending license review. |
| Device Tree Compiler (DTC) | `https://git.kernel.org/pub/scm/utils/dtc/dtc.git` | 2026-10-04 | `7a1e017926004ecff5fce62d62d42ce9f3e00082` | `4b81b3bc3af64a8ab7843c1f5a9adead57eea1b1fb2bd639ce67f0ac18b3d5f7` | Upstream DTC source; GPL-2.0-or-later. Built locally for standalone DTS validation. |
| Linux v6.18 DTS binding headers | `https://raw.githubusercontent.com/torvalds/linux/v6.18/include/` (individual paths under `dt-bindings/` and `uapi/linux/input-event-codes.h`) | 2026-10-04 | tag `v6.18` | See `reports/DTS-BUILD.md` for hashes of generated DTB; header files were fetched to `/tmp` and are not redistributed. | Official Linux source; GPL/BSD dual-licensed binding headers as individually marked. |

The OpenWrt technical reference names the 4.12L.06B release family for
BCM63168D0/Linux 2.6.30. The mirror's exact board-parameter entry matches
`963168MXH_17A`, but its relationship to the exact 2018 Zyxel build remains
unproven. See `hardware/boardparms-963168MXH_17A.md` and `DSL-PORT.md`.

Other consulted upstream references (web research, 2026-10-04):

- OpenWrt BCM63xx reference, including the 4.12L.06B and 4.16L.02A source
  families: <https://openwrt.org/docs/techref/hardware/soc/soc.broadcom.bcm63xx>
- Exact BCM63168D0 4.12L.06B archive linked by the OpenWrt reference:
  <https://osdn.net/projects/zyxel-vmg3312/downloads/68893/100AAPP7D0_4.12L.06B_consumer_release.tar.gz/>
  (direct workstation transfer was not possible on 2026-10-04 because
  `osdn.net` DNS resolution failed; the local Git mirror remains the inspected
  source and is not asserted byte-identical to this archive).
- BCM63168 Linux 3.4 `100AAJX8_4.16L.02A` archive link in the same reference:
  <https://drive.google.com/folderview?id=0B-U-Krbg5qbTfkEwYkFpUkhVNFhlU3hPeWlZSUlmNlppTkpsODlSbm5FOElyV1p3MENCZlk&usp=sharing>
  (archive not downloaded; the reference labels it as GPL plus closed code).
- OpenWrt package management: current 25.12+ uses apk; 24.10 and older use
  opkg: <https://openwrt.org/docs/guide-user/additional-software/managing_packages>
- OpenWrt current apk package recipe:
  <https://github.com/openwrt/openwrt/blob/main/package/system/apk/Makefile>
- Zyxel GPL source access and source-retention policy:
  <https://support.zyxel.eu/hc/en-us/articles/360017067100-Zyxel-Open-Source-Code-MyZyxelPortal-How-to-Access-Zyxel-Open-Source-Code-for-Programmers-GPL>
- Sky SR102 GPL source archive named by a public BCM63168 project:
  <http://oss.sky.com/SkyHD/SKY-IHR-2-1-s-3761-R-consumer-release.tar.gz>
  (connection timed out during read-only HEAD check on 2026-10-04; archive not
  downloaded). The GitHub project is not treated as a source artifact.
- Actiontec's official T1200 GPL page lists `bcm963xx_gpl_t07_consumer_release`
  (297 MB, firmware 31.128L.07/08), a BCM63168-family candidate. The page and
  presumed direct host both timed out from this workstation on 2026-10-04; no
  archive was downloaded. Recheck an accessible vendor-hosted copy before
  dismissing this lineage.
