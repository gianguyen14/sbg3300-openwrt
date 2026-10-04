# Vendor-source provenance

The local, Git-ignored source mirror is:

- Repository: `https://github.com/nomis/bcm963xx_4.12L.06B_consumer.git`
- Commit: `e2f23ddbb20bf75689372b6e6a5a0dc613f6e313`
- SHA256 of deterministic `git archive` at this commit:
  `6c1c585a44887ffcb824857ba2171cc8376139adfb79da7e6e220e629d272181`
- OpenWrt hardware reference names this source family for BCM63168D0,
  Linux 2.6.30, release `100AAPP7D0_4.12L.06B_consumer_release`.
- Mirror commit date: 2015-12-05. Current router kernel is a 2018 vendor build,
  so this is strong source-lineage evidence, not proof that every binary is
  byte/source-equivalent.

The tree is large and not committed here. Treat licensing carefully; proprietary
PHY/driver binaries must not be redistributed. Do not place the router's NVRAM,
MAC addresses, PPP credentials, calibration dump, keys, or tokens here.

An additional comparison mirror is also local and Git-ignored:

- Repository: `https://github.com/jclehner/bcmdrivers-gpl-bcm963xx.git`
- Commit: `1555117dd9e5b393cf5b92e10e603e1c5f8ba2bb`
- Deterministic `git archive` SHA256:
  `119904b6d458577bd9a45dec262423a527a020314c816b8f06099e4a6724c511`
- Its later `xtmrt/impl5` sources are comparison material, not an identified
  BCM63168/SBG3300 build; it contains no ADSL or XTM configuration driver tree.
