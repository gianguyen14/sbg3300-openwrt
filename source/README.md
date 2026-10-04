# Source checkout notes

`openwrt` is a symlink to `/home/nguyen/sbg3300-openwrt-source` because the
OpenWrt build system rejects any physical path containing spaces. The checkout
is the official `https://github.com/openwrt/openwrt.git` repository, branch
`main`, shallow-cloned at the revision recorded in `../reports/upstream-source.txt`.

The `vendor/` and `zyxel/` directories are for separately verified public
source releases. Do not put proprietary firmware blobs, credentials, or
per-device data in Git.
