#!/usr/bin/env bash
set -euo pipefail

if (( $# != 0 )); then
	echo "usage: $0" >&2
	exit 2
fi

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OPENWRT_DIR="${OPENWRT_DIR:-${XDG_CACHE_HOME:-${HOME:?Set HOME or OPENWRT_DIR}}/sbg3300-openwrt/port}"
EXPECTED_BASE="5edcc1c43cb97048b506168fbbe00538956796d6"
EXPECTED_PORT_TREE="2ac5b16d7ba20467a099bf096de89c32d69a9324"
JOBS="${JOBS:-3}"

if [[ ! -d "$OPENWRT_DIR/.git" ]]; then
	echo "OpenWrt checkout missing: $OPENWRT_DIR" >&2
	exit 1
fi

actual="$(git -C "$OPENWRT_DIR" rev-parse HEAD)"
tree="$(git -C "$OPENWRT_DIR" rev-parse 'HEAD^{tree}')"
if [[ "$tree" != "$EXPECTED_PORT_TREE" ]]; then
	echo "Expected tested port tree $EXPECTED_PORT_TREE; got $tree at $actual" >&2
	exit 1
fi
if [[ "$(git -C "$OPENWRT_DIR" merge-base HEAD "$EXPECTED_BASE")" != "$EXPECTED_BASE" ]]; then
	echo "Port commit does not descend from pinned upstream base" >&2
	exit 1
fi
if [[ -n "$(git -C "$OPENWRT_DIR" status --porcelain)" ]]; then
	echo "OpenWrt tracked worktree is dirty; refusing a non-reproducible build" >&2
	exit 1
fi

(cd "$OPENWRT_DIR" && ./scripts/feeds update -a && ./scripts/feeds install -a)

cp "$PROJECT_DIR/configs/sbg3300_port_defconfig" "$OPENWRT_DIR/.config"
make -C "$OPENWRT_DIR" defconfig
make -C "$OPENWRT_DIR" -j"$JOBS" V=s

ARTIFACT_DIR="$OPENWRT_DIR/bin/targets/bmips/bcm63268"
IMAGE="$ARTIFACT_DIR/openwrt-bmips-bcm63268-zyxel_sbg3300-n000-initramfs-OFFLINE-ONLY.elf"
MANIFEST="$ARTIFACT_DIR/openwrt-bmips-bcm63268-zyxel_sbg3300-n000.manifest"
DTB="$OPENWRT_DIR/build_dir/target-mips_mips32_musl/linux-bmips_bcm63268/image-bcm63168-zyxel-sbg3300-n000.dtb"
[[ -s "$IMAGE" && -s "$MANIFEST" && -s "$DTB" ]] || {
	echo "Expected SBG3300 offline artifacts are missing" >&2
	exit 1
}

DEST="$PROJECT_DIR/builds/sbg3300-offline-initramfs"
mkdir -p "$DEST/dts"
cp "$IMAGE" "$MANIFEST" "$DEST/"
cp "$DTB" "$DEST/dts/"
cp "$OPENWRT_DIR/.config" "$DEST/openwrt.config"
cp "$OPENWRT_DIR/build_dir/target-mips_mips32_musl/linux-bmips_bcm63268/linux-6.18.54/.config" "$DEST/kernel.config"
printf '%s\n' "$actual" > "$DEST/source-commit.txt"
find "$DEST" -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > "$DEST/SHA256SUMS"
(cd "$DEST" && sha256sum -c SHA256SUMS)

echo "Built SBG3300 profile at $actual"
echo "Status: OFFLINE-ONLY / NOT-FLASHABLE; no router interaction performed."
echo "Artifacts: $DEST"
