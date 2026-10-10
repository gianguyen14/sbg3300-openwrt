#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
UPSTREAM_URL="https://github.com/openwrt/openwrt.git"
UPSTREAM_COMMIT="5edcc1c43cb97048b506168fbbe00538956796d6"
PORT_TREE="b7b65a08d9af15f18f678aac38b471695fa3c1f8"
MODE="${1:-}"

case "$MODE" in
  baseline|port) ;;
  *) echo "usage: $0 baseline|port" >&2; exit 2 ;;
esac

CACHE_ROOT="${XDG_CACHE_HOME:-${HOME:?Set HOME or OPENWRT_DIR}}/sbg3300-openwrt"
DEFAULT_DIR="$CACHE_ROOT/$MODE"
OPENWRT_DIR="${OPENWRT_DIR:-$DEFAULT_DIR}"

if [[ "$OPENWRT_DIR" == *' '* ]]; then
  echo "OpenWrt rejects paths containing spaces: $OPENWRT_DIR" >&2
  echo "Set OPENWRT_DIR to a space-free path." >&2
  exit 1
fi

created=0
if [[ ! -e "$OPENWRT_DIR" ]]; then
  mkdir -p "$(dirname "$OPENWRT_DIR")"
  git clone --filter=blob:none --no-checkout "$UPSTREAM_URL" "$OPENWRT_DIR"
  created=1
fi

if [[ ! -d "$OPENWRT_DIR/.git" ]]; then
  echo "Refusing non-Git checkout path: $OPENWRT_DIR" >&2
  exit 1
fi

origin="$(git -C "$OPENWRT_DIR" remote get-url origin)"
if [[ "$origin" != "$UPSTREAM_URL" ]]; then
  echo "Unexpected origin: $origin" >&2
  exit 1
fi

git -C "$OPENWRT_DIR" reset --hard

actual="$(git -C "$OPENWRT_DIR" rev-parse HEAD 2>/dev/null || true)"
if [[ "$MODE" == baseline ]]; then
  if [[ "$actual" != "$UPSTREAM_COMMIT" ]]; then
    if [[ -n "$actual" && "$created" -eq 0 ]]; then
      echo "Unexpected existing commit $actual; use a fresh OPENWRT_DIR." >&2
      exit 1
    fi
    git -C "$OPENWRT_DIR" fetch --depth=1 origin "$UPSTREAM_COMMIT"
    git -C "$OPENWRT_DIR" checkout --detach "$UPSTREAM_COMMIT"
  fi
else
  if [[ -n "$actual" ]]; then
    actual_tree="$(git -C "$OPENWRT_DIR" rev-parse 'HEAD^{tree}')"
    if [[ "$actual_tree" == "$PORT_TREE" ]]; then
      echo "SBG3300 patch tree is already prepared: $actual ($actual_tree)"
      exit 0
    fi
  fi
  if [[ -n "$actual" && "$actual" != "$UPSTREAM_COMMIT" && "$created" -eq 0 ]]; then
    echo "Unexpected existing commit $actual; use a fresh OPENWRT_DIR." >&2
    exit 1
  fi
  if [[ "$actual" != "$UPSTREAM_COMMIT" ]]; then
    git -C "$OPENWRT_DIR" fetch --depth=1 origin "$UPSTREAM_COMMIT"
    git -C "$OPENWRT_DIR" checkout --detach "$UPSTREAM_COMMIT"
  fi
  git -C "$OPENWRT_DIR" switch -c zyxel-sbg3300-port
  while IFS= read -r patch_name; do
    [[ -z "$patch_name" || "$patch_name" == \#* ]] && continue
    git -C "$OPENWRT_DIR" am "$PROJECT_ROOT/patches/openwrt/$patch_name"
  done < "$PROJECT_ROOT/patches/openwrt/series"
  actual="$(git -C "$OPENWRT_DIR" rev-parse HEAD)"
  actual_tree="$(git -C "$OPENWRT_DIR" rev-parse 'HEAD^{tree}')"
  if [[ "$actual_tree" != "$PORT_TREE" ]]; then
    echo "Patch series produced unexpected tree: $actual_tree (expected $PORT_TREE)" >&2
    exit 1
  fi
fi

if [[ -n "$(git -C "$OPENWRT_DIR" status --porcelain)" ]]; then
  echo "Prepared source is unexpectedly dirty" >&2
  exit 1
fi

printf 'Prepared %s source: %s\nCommit: %s\n' "$MODE" "$OPENWRT_DIR" "$actual"
