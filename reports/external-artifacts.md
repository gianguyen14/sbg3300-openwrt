# External source artifacts

Hashes below are SHA256 of a deterministic uncompressed `git archive` of the
recorded commit. They fingerprint tracked source at that commit; they are not
hashes of repository metadata or untracked/local files.

| Artifact | URL | Retrieved | Revision | Archive SHA256 | Trust / license |
|---|---|---|---|---|---|
| OpenWrt | `https://github.com/openwrt/openwrt.git` | 2026-10-04 | `5edcc1c43cb97048b506168fbbe00538956796d6` (`main`) | `c7aaab7ff18de097fbfdc304763e2c9c25a564486932b3a8b08302b8076891a0` | Official upstream; OpenWrt project licensing applies |
| BCM963xx 4.12L.06B consumer source mirror | `https://github.com/nomis/bcm963xx_4.12L.06B_consumer.git` | 2026-10-04 | `e2f23ddbb20bf75689372b6e6a5a0dc613f6e313` | `6c1c585a44887ffcb824857ba2171cc8376139adfb79da7e6e220e629d272181` | Secondary public mirror; source tree's redistribution/licensing terms are not yet audited. Keep local-only; do not redistribute proprietary objects/blobs. |

The OpenWrt technical reference names the 4.12L.06B release family for
BCM63168D0/Linux 2.6.30. The mirror's exact board-parameter entry matches
`963168MXH_17A`, but its relationship to the exact 2018 Zyxel build remains
unproven. See `hardware/boardparms-963168MXH_17A.md` and `DSL-PORT.md`.
