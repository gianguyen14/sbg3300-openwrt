#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-or-later
# External module compilation only. Never installs or loads the result.
set -euo pipefail
project_dir="$(cd "$(dirname "$0")/.." && pwd)"
openwrt_dir="${OPENWRT_DIR:-$HOME/sbg3300-openwrt-source}"
kernel_dir="${KERNEL_DIR:?Set KERNEL_DIR to a verified Linux 6.18.54 build}"
evidence_root="${ENETSW_BUILD_ROOT:-$HOME/.cache/sbg3300-enetsw-validation}"
cross="$openwrt_dir/staging_dir/toolchain-mips_mips32_gcc-14.4.0_musl/bin/mips-openwrt-linux-musl-"
export STAGING_DIR="$openwrt_dir/staging_dir/target-mips_mips32_musl"
test -x "${cross}gcc"
for setting in CONFIG_32BIT=y CONFIG_CPU_BIG_ENDIAN=y CONFIG_CPU_BMIPS=y; do
  rg -F -x -q "$setting" "$kernel_dir/.config"
done
rg -q '^#define UTS_RELEASE "6\.18\.54"$' "$kernel_dir/include/generated/utsrelease.h"
mkdir -p "$evidence_root"
run_dir="$(mktemp -d "$evidence_root/run-XXXXXX")"
sha256sum "$kernel_dir/"{.config,Module.symvers,vmlinux,include/generated/utsrelease.h} \
  > "$run_dir/preserved-kernel.sha256"
trap 'sha256sum -c "$run_dir/preserved-kernel.sha256"' EXIT
source_rel=drivers/net/ethernet/broadcom
mkdir -p "$run_dir/source/$source_rel"
cp "$kernel_dir/$source_rel/bcm6368-enetsw.c" "$run_dir/source/$source_rel/"
if [[ -e "$kernel_dir/$source_rel/enetsw_contract.h" ]]; then
  cp "$kernel_dir/$source_rel/enetsw_contract.h" "$run_dir/source/$source_rel/"
fi
for delta in 0003-bcm6368-enetsw-managed-lifetime.patch 0004-bcm6368-enetsw-rx-poll.patch; do
  patch_file="$project_dir/integration/schema-patches/$delta"
  if patch -d "$run_dir/source" -p1 --batch --forward --dry-run \
      < "$patch_file" >> "$run_dir/patch-application.log" 2>&1; then
    patch -d "$run_dir/source" -p1 --batch --forward \
      < "$patch_file" >> "$run_dir/patch-application.log" 2>&1
  else
    patch -d "$run_dir/source" -p1 --batch --reverse --dry-run \
      < "$patch_file" >> "$run_dir/patch-application.log" 2>&1
  fi
done
cmp "$project_dir/drivers/ethernet/enetsw_contract.h" \
  "$run_dir/source/$source_rel/enetsw_contract.h"
sha256sum "$run_dir/source/$source_rel/"* > "$run_dir/source.sha256"
for build in one two; do
  module_dir="$run_dir/$build"
  mkdir "$module_dir"
  cp "$run_dir/source/$source_rel/"* "$module_dir/"
  printf 'obj-m := bcm6368-enetsw.o\n' > "$module_dir/Makefile"
  set +e
  make -C "$kernel_dir" M="$module_dir" ARCH=mips CROSS_COMPILE="$cross" \
    W=1 "KCFLAGS=-Werror -ffile-prefix-map=$module_dir=/build/enetsw -ffile-prefix-map=$kernel_dir=/build/kernel" \
    modules V=1 > "$run_dir/$build-compiler-modpost.log" 2>&1
  result=$?
  set -e
  printf '%s\n' "$result" > "$run_dir/$build.exit"
  (( result == 0 )) || { printf 'Failed build %s: %s\n' "$build" "$run_dir" >&2; exit "$result"; }
  python3 "$project_dir/tools/audit-kernel-artifacts.py" --symvers "$kernel_dir/Module.symvers" \
    "$module_dir/bcm6368-enetsw.ko" > "$run_dir/$build-audit.json"
done
cmp "$run_dir/one/bcm6368-enetsw.ko" "$run_dir/two/bcm6368-enetsw.ko"
sha256sum "$run_dir/"{one,two}/bcm6368-enetsw.ko > "$run_dir/modules.sha256"
printf 'Strict real compiler/modpost and byte reproduction passed: %s\n' "$run_dir"
