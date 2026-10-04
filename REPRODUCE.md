# Reproduce the offline OpenWrt work

These commands use only public OpenWrt source and checked-in project patches.
They do not access a router. All resulting images are for offline research and
must not be flashed.

## Requirements

Linux x86_64, Git, internet access, standard OpenWrt build dependencies, and
substantial free disk/RAM. OpenWrt prerequisite checks reject source paths
containing spaces. The default checkout is under `$HOME/.cache/sbg3300-openwrt`
and can be overridden with a space-free `OPENWRT_DIR`.

## Clone and inspect

```sh
git clone https://github.com/gianguyen14/sbg3300-openwrt.git
cd sbg3300-openwrt
cat AGENTS.md STATUS.md HANDOFF-HERMES.md
```

## Prepare pinned source

```sh
tools/prepare-openwrt.sh baseline
```

This clones the official upstream repository at the pinned commit and checks
its origin, revision, and cleanliness. To choose a different space-free path:

```sh
OPENWRT_DIR=/tmp/openwrt-bmips-baseline tools/prepare-openwrt.sh baseline
```

## Build unmodified baseline

```sh
OPENWRT_DIR="$HOME/.cache/sbg3300-openwrt/baseline" \
  tools/build-openwrt.sh baseline
```

Baseline output covers existing bmips/bcm63268 profiles. Any sibling-router
image is unrelated to SBG3300 and must never be used on it.

## Prepare and build the SBG3300 profile

Use a separate checkout from the baseline:

```sh
tools/prepare-openwrt.sh port
OPENWRT_DIR="$HOME/.cache/sbg3300-openwrt/port" \
  tools/build-sbg3300-profile.sh
```

The `port` preparation applies `patches/openwrt/series` in order to the exact
pinned base and checks the expected resulting source tree (commit IDs can vary
because `git am` records the local committer time). It does not produce a
factory or sysupgrade recipe. The only SBG3300 artifact is named
`*-initramfs-OFFLINE-ONLY.elf` and is not known to be loadable by CFE.

The profile build archives local output under ignored `builds/` and records
SHA256 sums. Verify them from the project root:

```sh
(cd builds/sbg3300-offline-initramfs && sha256sum -c SHA256SUMS)
file builds/sbg3300-offline-initramfs/*OFFLINE-ONLY.elf
sha256sum builds/sbg3300-offline-initramfs/*OFFLINE-ONLY.elf
```

Hashes can vary if source/config/toolchain inputs change. Record exact new
values rather than copying a previous hash.

## Patch/DTS checks without a full build

```sh
OPENWRT_DIR="$HOME/.cache/sbg3300-openwrt/port" \
  tools/prepare-openwrt.sh port
git -C "$HOME/.cache/sbg3300-openwrt/port" status --short
```

For a clean independent patch check, create a fresh checkout with the `port`
mode script; it runs `git am` for the checked-in series. If the expected patch
head or base differs, stop and inspect rather than force-resetting an existing
worktree.

The documented baseline/profile full builds are prior `BUILD-RESULT` evidence;
rebuilding is optional when only documentation changed. Current reports are
under `reports/`. Local logs and generated build trees are intentionally not
tracked.
