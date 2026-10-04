# Source checkout notes

The local `openwrt` checkout is ignored by Git. OpenWrt rejects source paths
containing spaces; use `tools/prepare-openwrt.sh` or set `OPENWRT_DIR` to a
space-free path. The checkout is the official
`https://github.com/openwrt/openwrt.git` repository at the pinned revision in
`../reports/upstream-source.txt`.

The `vendor/` and `zyxel/` directories are for separately verified public
source releases. Do not put proprietary firmware blobs, credentials, or
per-device data in Git.
