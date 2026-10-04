# Stable baseline snapshot

Created in this isolated OpenWrt R&D project before port changes. The live
router was not modified; snapshot material was copied from the existing
STABLE-V1 archive and has restrictive local permissions. It is local-only and
ignored by Git.

Primary artifacts:

| Artifact | SHA256 |
|---|---|
| Canonical stock firmware | `3b994309aec554c858d8129c17ff1966b11ec33cb9f3e77914bcf211f0310b79` |
| Known-good stock-custom firmware candidate | `9957eae1364e9df3f64fd6524a84b5ac9fd03125d33e4bc7c91da9cd2c9a09a1` |
| Persistent security-layer archive | `a6e6ba82bd0e202756e6d477853f606c5ae21d1a3c82346f776e4f3330b2635c` |
| Sanitized custom-layer archive | `ecddae428b6883ec65d68b66abaac3a7de0ab5d0bcdbd2221318007dc3597b2a` |

The snapshot contains the stock and known-good firmware artifacts, extracted
stock rootfs archive, sanitized custom/security backups, pre-port router
snapshots, and the original STABLE-V1 manifest. A fresh project-local
`backups/STABLE-V1-SNAPSHOT.sha256` was generated over the copied tree and
verified with `sha256sum -c`.

The original archived manifest contains stale entries for the manifest itself
and one router snapshot file; those two old entries do not verify against the
archived files. The files were not changed during this project copy (the
copied snapshot compares byte-for-byte with its source). The fresh local
manifest covers the actual snapshot bytes and verifies. This discrepancy is
recorded rather than silently rewriting the historical manifest.

No device credential, PPP secret, token, calibration data, or live NVRAM dump
was added to source control. Firmware/rootfs and backup archives remain
permission-restricted on the workstation.
