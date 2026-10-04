#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OPENWRT_DIR="${OPENWRT_DIR:-${XDG_CACHE_HOME:-${HOME:?Set HOME or OPENWRT_DIR}}/sbg3300-openwrt/baseline}"
EXPECTED_COMMIT="5edcc1c43cb97048b506168fbbe00538956796d6"
JOBS="${JOBS:-3}"
MODE="${1:-baseline}"

case "$MODE" in
  baseline) ;;
  *) echo "usage: $0 [baseline]" >&2; exit 2 ;;
esac

if [[ ! -d "$OPENWRT_DIR/.git" ]]; then
  echo "OpenWrt checkout missing: $OPENWRT_DIR" >&2
  exit 1
fi
if [[ "$OPENWRT_DIR" == *' '* ]]; then
  echo "OpenWrt refuses source paths containing spaces" >&2
  exit 1
fi
actual="$(git -C "$OPENWRT_DIR" rev-parse HEAD)"
if [[ "$actual" != "$EXPECTED_COMMIT" ]]; then
  echo "Unexpected OpenWrt commit: $actual" >&2
  exit 1
fi

if [[ -n "$(git -C "$OPENWRT_DIR" status --porcelain)" ]]; then
  echo "OpenWrt tracked worktree is dirty; refusing a non-reproducible build" >&2
  exit 1
fi

(cd "$OPENWRT_DIR" && ./scripts/feeds update -a && ./scripts/feeds install -a)

cp "$PROJECT_DIR/configs/sbg3300_defconfig" "$OPENWRT_DIR/.config"
make -C "$OPENWRT_DIR" defconfig
make -C "$OPENWRT_DIR" -j"$JOBS" V=s

DEST="$PROJECT_DIR/builds/upstream-bmips-bcm63268-baseline"
mkdir -p "$DEST"
cp "$OPENWRT_DIR/.config" "$DEST/config"
ARTIFACT_DIR="$OPENWRT_DIR/bin/targets/bmips/bcm63268"
mapfile -t artifacts < <(find "$ARTIFACT_DIR" -maxdepth 1 -type f -print | sort)
if (( ${#artifacts[@]} == 0 )); then
  echo "No bmips/bcm63268 baseline artifacts found in $ARTIFACT_DIR" >&2
  exit 1
fi
cp -- "${artifacts[@]}" "$DEST/"
find "$DEST" -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 -r sha256sum > "$DEST/SHA256SUMS"
printf 'Built unmodified upstream baseline at commit %s\n' "$actual"
printf 'Artifacts: %s\n' "$DEST"
printf 'Status: OFFLINE-ONLY; no SBG3300 image support or flash approval implied.\n'
