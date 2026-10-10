#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
set -euo pipefail
project_dir="$(cd "$(dirname "$0")/.." && pwd)"
destination="${1:?Usage: stage-xtm-package.sh ISOLATED_OPENWRT_TREE}"
test -f "$destination/include/kernel.mk"
test -f "$destination/rules.mk"
package_dir="$destination/package/kernel/sbg3300-xtm"
# Keep a single public implementation; populate a new staging package only.
test ! -e "$package_dir" || { echo 'Package destination exists' >&2; exit 1; }
mkdir -p "$package_dir/src"
cp "$project_dir/integration/openwrt/sbg3300-xtm/Makefile" "$package_dir/"
cp "$project_dir/drivers/xtm/"{Makefile,COPYING,xtm_core.c,xtm_core.h,xtm_dma.c,xtm_dma.h,xtm_ptm.c,xtm_ptm.h,xtm_ptm_core.c,xtm_ptm_core.h} "$package_dir/src/"
printf 'Staged package: %s\n' "$package_dir"
