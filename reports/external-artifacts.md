# External source artifacts

Hashes below are SHA256 of a deterministic uncompressed `git archive` of the
recorded commit. They fingerprint tracked source at that commit; they are not
hashes of repository metadata or untracked/local files.

| Artifact | URL | Retrieved | Revision | Archive SHA256 | Trust / license |
|---|---|---|---|---|---|
| OpenWrt | `https://github.com/openwrt/openwrt.git` | 2026-10-04 | `5edcc1c43cb97048b506168fbbe00538956796d6` (`main`) | `c7aaab7ff18de097fbfdc304763e2c9c25a564486932b3a8b08302b8076891a0` | Official upstream; OpenWrt project licensing applies |
| BCM963xx 4.12L.06B consumer source mirror | `https://github.com/nomis/bcm963xx_4.12L.06B_consumer.git` | 2026-10-04 | `e2f23ddbb20bf75689372b6e6a5a0dc613f6e313` | `6c1c585a44887ffcb824857ba2171cc8376139adfb79da7e6e220e629d272181` | Secondary public mirror; source tree's redistribution/licensing terms are not yet audited. Keep local-only; do not redistribute proprietary objects/blobs. |
| Broadcom GPL driver comparison tree | `https://github.com/jclehner/bcmdrivers-gpl-bcm963xx.git` | 2026-10-04 | `1555117dd9e5b393cf5b92e10e603e1c5f8ba2bb` | `119904b6d458577bd9a45dec262423a527a020314c816b8f06099e4a6724c511` | Secondary mirror, later/non-matching SoC lineage; useful XTM comparison only, no ADSL or XTM-config driver sources. Local-only pending license review. |

The OpenWrt technical reference names the 4.12L.06B release family for
BCM63168D0/Linux 2.6.30. The mirror's exact board-parameter entry matches
`963168MXH_17A`, but its relationship to the exact 2018 Zyxel build remains
unproven. See `hardware/boardparms-963168MXH_17A.md` and `DSL-PORT.md`.

Other consulted upstream references (web research, 2026-10-04):

- OpenWrt BCM63xx reference, including the 4.12L.06B and 4.16L.02A source
  families: <https://openwrt.org/docs/techref/hardware/soc/soc.broadcom.bcm63xx>
- OpenWrt package management: current 25.12+ uses apk; 24.10 and older use
  opkg: <https://openwrt.org/docs/guide-user/additional-software/managing_packages>
- OpenWrt current apk package recipe:
  <https://github.com/openwrt/openwrt/blob/main/package/system/apk/Makefile>
- Zyxel GPL source access and source-retention policy:
  <https://support.zyxel.eu/hc/en-us/articles/360017067100-Zyxel-Open-Source-Code-MyZyxelPortal-How-to-Access-Zyxel-Open-Source-Code-for-Programmers-GPL>
