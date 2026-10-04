# Artifact inventory

Generated firmware, stock images, extracted rootfs, and large build outputs
are intentionally not committed. Current ignored local material may exist on
the original workstation only.

| Artifact | Exists locally? | In Git? | Public-safe decision | Status / identity |
|---|---:|---:|---|---|
| Canonical Zyxel stock firmware | Yes, local-only | No | Do not publish | SHA256 `3b994309aec554c858d8129c17ff1966b11ec33cb9f3e77914bcf211f0310b79`; proprietary firmware |
| Stock-mod firmware candidate | Yes, local-only backup | No | Do not publish | Device project recovery artifact |
| Extracted stock rootfs/kernel/modules | Yes, local-only | No | Do not publish | Proprietary; contains device firmware material |
| STABLE-V1 snapshot/router data | Yes, local-only | No | Do not publish | May include identifying/configuration data; sanitized project metadata only |
| OpenWrt source checkout | Yes, ignored checkout | No | Fetch from upstream | Official pinned source, commit in `STATUS.md` |
| Unmodified bmips baseline images | Yes, ignored build output | No | Not published | Sibling-board images are not SBG3300 firmware |
| SBG3300 initramfs ELF | Yes, ignored local artifact | No | No release upload in this publication | SHA256 `3961a39d5d554ce467b9575bbc6f6293d385ddda9fc4dc9b3dbf0c3cf8027b51`; OFFLINE-ONLY, NOT-FLASHABLE |
| SBG3300 DTB | Yes, ignored local artifact | No | Not required for repo | SHA256 `e6e680e875e0f1251eb7d3c2f355acc2dc94e2bc909aa1d5fff2af5a4baa90fb`; compile evidence only |
| OpenWrt patches, DTS source, configs, tools, reports | Yes | Yes | Public project source/docs | No secrets or proprietary blobs intended |
| RD-1 tarball | Yes, local-only | No | Do not attach to GitHub release in this publication; artifact audit/licensing confidence is not treated as a substitute for source/legal review | Contents listed in local release tree; no stock firmware found in its member list |

## Important distinctions

- A sibling BCM63268 baseline image is not an SBG3300 firmware.
- The SBG3300 initramfs ELF is not a stock-web factory image.
- A factory-container validator pass, if later obtained, would not prove
  runtime boot or safe NAND behavior.
- No item is currently marked flashable.

The release tarball decision and public-material scan are recorded in
`reports/RELEASE-PUBLICATION.md` and `reports/PUBLIC-REPO-SAFETY.md`.
