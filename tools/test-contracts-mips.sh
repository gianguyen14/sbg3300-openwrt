#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
# CPU-only user-mode emulation. No kernel/module loading or router operation.
set -euo pipefail
project_dir="$(cd "$(dirname "$0")/.." && pwd)"
openwrt_dir="${OPENWRT_DIR:-$HOME/sbg3300-openwrt-source}"
cross="$openwrt_dir/staging_dir/toolchain-mips_mips32_gcc-14.4.0_musl/bin/mips-openwrt-linux-musl-"
export STAGING_DIR="$openwrt_dir/staging_dir/target-mips_mips32_musl"
emulator="${QEMU_MIPS:-qemu-mips-static}"
command -v "$emulator" >/dev/null
evidence_root="${CONTRACT_TEST_ROOT:-$HOME/.cache/sbg3300-mips-contract-tests}"
mkdir -p "$evidence_root"
run_dir="$(mktemp -d "$evidence_root/run-XXXXXX")"
"${cross}gcc" -static -std=c11 -Wall -Wextra -Werror \
  "$project_dir/drivers/xtm/xtm_core.c" "$project_dir/tests/test_xtm_core.c" \
  -o "$run_dir/xtm-core"
"${cross}gcc" -static -std=c11 -Wall -Wextra -Werror \
  "$project_dir/drivers/xtm/xtm_ptm_core.c" "$project_dir/tests/test_xtm_ptm.c" \
  -o "$run_dir/ptm-core"
"${cross}gcc" -static -std=c11 -Wall -Wextra -Werror \
  "$project_dir/tests/test_enetsw_contract.c" -o "$run_dir/enetsw-contract"
for test_binary in xtm-core ptm-core enetsw-contract; do
  "$emulator" "$run_dir/$test_binary" > "$run_dir/$test_binary.log" 2>&1
  cat "$run_dir/$test_binary.log"
done
python3 "$project_dir/tools/audit-kernel-artifacts.py" \
  "$run_dir/xtm-core" "$run_dir/ptm-core" "$run_dir/enetsw-contract" \
  > "$run_dir/artifacts.json"
printf 'MIPS user-mode tests passed; no hardware evidence. Artifacts: %s\n' "$run_dir"
