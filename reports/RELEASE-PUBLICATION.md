# RD-1 publication decision

The local `OPENWRT-RD-1-NOT-FLASHABLE` tarball was enumerated and its complete
member list reviewed. It contains the offline initramfs ELF and DTB, project
patches, config, selected sanitized reports/docs, and build helper. The member
list did not show stock firmware, extracted proprietary modules, calibration,
credentials, or private keys.

**Decision: do not upload the tarball or create a GitHub binary release in this
publication.** The public source relationship and redistribution conditions
for every linked/generated binary component have not been reviewed to a level
that justifies publishing a binary bundle. The repository will publish source,
patches, reproducible instructions, hashes, and sanitized evidence only. The
artifact remains local and `OFFLINE-ONLY`, `NOT-FLASHABLE`.

The source repository/tag is the public milestone. This decision does not
assert that the binary is unsafe; it is a conservative provenance/licensing
boundary.
