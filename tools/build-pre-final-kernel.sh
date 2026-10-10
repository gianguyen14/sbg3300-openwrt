#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
# Kernel-only compile coverage; deliberately contains no OpenWrt image target.
set -euo pipefail
project_dir="$(cd "$(dirname "$0")/.." && pwd)"
openwrt_dir="${OPENWRT_DIR:-$HOME/sbg3300-openwrt-source}"
evidence_root="${PRE_FINAL_BUILD_ROOT:-$HOME/.cache/sbg3300-pre-final-kernel}"
pinned=5edcc1c43cb97048b506168fbbe00538956796d6
approved=18c17336871e73ddfbab3198104d8c42df844146
source_sha="$(git -C "$openwrt_dir" rev-parse HEAD)"
source_tree="$(git -C "$openwrt_dir" rev-parse 'HEAD^{tree}')"
case "$source_sha:$source_tree" in
  "$pinned:"*|"$approved:"*|*:2ac5b16d7ba20467a099bf096de89c32d69a9324|*:4769e1aa08793c94a990092080d6db094d67a30f) ;;
  *) exit 1 ;;
esac
test "$(git -C "$openwrt_dir" merge-base HEAD "$pinned")" = "$pinned"
test -z "$(git -C "$openwrt_dir" status --porcelain)"
original="$openwrt_dir/build_dir/target-mips_mips32_musl/linux-bmips_bcm63268/linux-6.18.54"
kernel_base="${KERNEL_BASE:-$original}"
cross="$openwrt_dir/staging_dir/toolchain-mips_mips32_gcc-14.4.0_musl/bin/mips-openwrt-linux-musl-"
export STAGING_DIR="$openwrt_dir/staging_dir/target-mips_mips32_musl"
test -x "${cross}gcc"
mkdir -p "$evidence_root"
run_dir="$(mktemp -d "$evidence_root/run-XXXXXX")"
sha256sum "$kernel_base/"{.config,Module.symvers,vmlinux,include/generated/utsrelease.h} \
  > "$run_dir/preserved-kernel.sha256"
trap 'sha256sum -c "$run_dir/preserved-kernel.sha256"' EXIT
cp -a --reflink=auto "$kernel_base" "$run_dir/kernel"
kernel="$run_dir/kernel"
# Each delta must apply to the preserved unmodified kernel source. If the
# kernel was already patched, use that prepared tree directly instead.
for patch in 0001-brcm-sbg3300-compatible.patch 0002-bcm63268-resource-bindings.patch \
             0003-bcm6368-enetsw-managed-lifetime.patch \
             0004-bcm6368-enetsw-rx-poll.patch; do
  if patch -d "$kernel" -p1 --batch --forward --dry-run \
      < "$project_dir/integration/schema-patches/$patch" \
      >> "$run_dir/patch-application.log" 2>&1; then
    patch -d "$kernel" -p1 --batch --forward \
      < "$project_dir/integration/schema-patches/$patch" \
      >> "$run_dir/patch-application.log" 2>&1
  else
    patch -d "$kernel" -p1 --batch --reverse --dry-run \
      < "$project_dir/integration/schema-patches/$patch" \
      >> "$run_dir/patch-application.log" 2>&1
  fi
done
cmp "$project_dir/drivers/ethernet/enetsw_contract.h" \
  "$kernel/drivers/net/ethernet/broadcom/enetsw_contract.h"
printf '%s\n' "$source_sha" > "$run_dir/openwrt-revision.txt"
cp "$project_dir/configs/kernel-pre-final.fragment" "$run_dir/coverage.fragment"
(cd "$kernel"; scripts/kconfig/merge_config.sh -m .config "$run_dir/coverage.fragment") \
  > "$run_dir/config-merge.log" 2>&1
make -C "$kernel" ARCH=mips CROSS_COMPILE="$cross" olddefconfig \
  > "$run_dir/config.log" 2>&1
# Kconfig may silently drop symbols with unsatisfied dependencies: reject that.
while IFS= read -r setting; do
  if [[ "$setting" == CONFIG_*=* ]]; then
    :
  elif [[ "$setting" =~ ^#\ CONFIG_[A-Z0-9_]+\ is\ not\ set$ ]]; then
    : # Explicit negative coverage settings must survive Kconfig too.
  else
    continue
  fi
  rg -F -x -q "$setting" "$kernel/.config" || {
    printf 'Missing requested setting: %s\nEvidence: %s\n' "$setting" "$run_dir" >&2
    exit 1
  }
done < "$run_dir/coverage.fragment"
rg -q '^#define UTS_RELEASE "6\.18\.54"$' "$kernel/include/generated/utsrelease.h"
set +e
make -C "$kernel" -j"${JOBS:-3}" ARCH=mips CROSS_COMPILE="$cross" \
  KBUILD_BUILD_USER=builder KBUILD_BUILD_HOST=offline \
  SOURCE_DATE_EPOCH=1791086400 KBUILD_BUILD_TIMESTAMP='2026-10-04 04:00:00 UTC' \
  vmlinux modules V=1 > "$run_dir/compiler-modpost.log" 2>&1
result=$?
set -e
printf '%s\n' "$result" > "$run_dir/build.exit"
printf 'Evidence: %s\nKernel/modules exit: %s\n' "$run_dir" "$result"
if (( result == 0 )); then
  mapfile -d '' modules < <(find "$kernel" -type f -name '*.ko' -print0 | sort -z)
  python3 "$project_dir/tools/audit-kernel-artifacts.py" --symvers "$kernel/Module.symvers" \
    "$kernel/vmlinux" "${modules[@]}" > "$run_dir/artifact-audit.json"
fi
exit "$result"
