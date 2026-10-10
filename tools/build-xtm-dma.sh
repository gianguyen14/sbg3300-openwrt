#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
set -euo pipefail
project_dir="$(cd "$(dirname "$0")/.." && pwd)"
openwrt_dir="${OPENWRT_DIR:-$HOME/sbg3300-openwrt-source}"
evidence_root="${XTM_BUILD_ROOT:-$HOME/.cache/sbg3300-xtm-runtime}"
pinned=5edcc1c43cb97048b506168fbbe00538956796d6
tested_port=18c17336871e73ddfbab3198104d8c42df844146
source_sha="$(git -C "$openwrt_dir" rev-parse HEAD)"
case "$source_sha" in
  "$pinned"|"$tested_port") ;;
  *) echo "Unapproved source revision: $source_sha" >&2; exit 1 ;;
esac
test "$(git -C "$openwrt_dir" merge-base HEAD "$pinned")" = "$pinned"
test -z "$(git -C "$openwrt_dir" status --porcelain)"
kernel_dir="${KERNEL_DIR:-$openwrt_dir/build_dir/target-mips_mips32_musl/linux-bmips_bcm63268/linux-6.18.54}"
cross="$openwrt_dir/staging_dir/toolchain-mips_mips32_gcc-14.4.0_musl/bin/mips-openwrt-linux-musl-"
export STAGING_DIR="$openwrt_dir/staging_dir/target-mips_mips32_musl"
test -x "${cross}gcc"
test -x "$kernel_dir/scripts/mod/modpost"
for f in .config Module.symvers vmlinux include/generated/utsrelease.h; do
  test -s "$kernel_dir/$f"
done
rg -q '^#define UTS_RELEASE "6\.18\.54"$' "$kernel_dir/include/generated/utsrelease.h"
for option in MODULES CPU_BIG_ENDIAN CPU_BMIPS4350 32BIT; do
  rg -q "^CONFIG_${option}=y$" "$kernel_dir/.config"
done
mkdir -p "$evidence_root"
run_dir="$(mktemp -d "$evidence_root/run-XXXXXX")"
mkdir "$run_dir/module"
cp "$project_dir/drivers/xtm/"{Makefile,xtm_core.c,xtm_core.h,xtm_dma.c,xtm_dma.h,xtm_ptm.c,xtm_ptm.h,xtm_ptm_core.c,xtm_ptm_core.h} "$run_dir/module/"
python3 - "$run_dir/module" > "$run_dir/source-inputs.json" <<'PY'
import hashlib, json, pathlib, sys
root = pathlib.Path(sys.argv[1])
print(json.dumps({p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in sorted(root.iterdir())}, indent=2, sort_keys=True))
PY
snapshot() {
  python3 - "$kernel_dir" <<'PY'
import hashlib, json, pathlib, sys
root = pathlib.Path(sys.argv[1])
names = ['.config', 'Module.symvers', 'vmlinux', 'include/generated/utsrelease.h']
print(json.dumps({name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                  for name in names}, indent=2, sort_keys=True))
PY
}
snapshot > "$run_dir/kernel-inputs-before.json"
git -C "$project_dir" rev-parse HEAD > "$run_dir/project-revision.txt"
printf '%s\n' "$source_sha" > "$run_dir/openwrt-revision.txt"
"${cross}gcc" --version > "$run_dir/compiler-version.txt"
date -u +%FT%TZ > "$run_dir/start-utc.txt"
set +e
make -C "$kernel_dir" M="$run_dir/module" ARCH=mips CROSS_COMPILE="$cross" \
  W=1 "KCFLAGS=-Werror -ffile-prefix-map=$run_dir/module=/build/xtm -ffile-prefix-map=$kernel_dir=/build/kernel" \
  KBUILD_BUILD_USER=builder KBUILD_BUILD_HOST=offline \
  KBUILD_BUILD_TIMESTAMP='2026-10-04 04:00:00 UTC' V=1 modules \
  > "$run_dir/compiler-modpost.log" 2>&1
build_rc=$?
set -e
date -u +%FT%TZ > "$run_dir/end-utc.txt"
printf '%s\n' "$build_rc" > "$run_dir/build.exit"
snapshot > "$run_dir/kernel-inputs-after.json"
cmp "$run_dir/kernel-inputs-before.json" "$run_dir/kernel-inputs-after.json" || {
  echo "Kernel inputs changed during external build; evidence: $run_dir" >&2
  exit 1
}
if (( build_rc == 0 )); then
  module="$run_dir/module/sbg3300_xtm_dma.ko"
  test -s "$module"
  "${cross}readelf" -h "$module" > "$run_dir/elf-header.txt"
  "${cross}readelf" -p .modinfo "$module" > "$run_dir/modinfo.txt"
  "${cross}nm" -u "$module" > "$run_dir/undefined-symbols.txt"
  sha256sum "$module" > "$run_dir/module.sha256"
  python3 - "$run_dir" "$kernel_dir/Module.symvers" <<'PY'
import json, pathlib, sys
run = pathlib.Path(sys.argv[1])
exports = {line.split()[1] for line in pathlib.Path(sys.argv[2]).read_text().splitlines()}
imports = {line.split()[-1] for line in (run / 'undefined-symbols.txt').read_text().splitlines()}
missing = sorted(imports - exports)
report = {'kernel_import_count': len(imports), 'missing_from_kernel_exports': missing}
(run / 'symbol-audit.json').write_text(json.dumps(report, indent=2) + '\n')
if missing:
    raise SystemExit('Module imports absent from pinned kernel exports')
modinfo = (run / 'modinfo.txt').read_text()
if 'vermagic=6.18.54 SMP mod_unload BMIPS 32BIT' not in modinfo:
    raise SystemExit('Unexpected vermagic')
elf = (run / 'elf-header.txt').read_text()
for token in ['ELF32', 'big endian', 'MIPS', 'o32']:
    if token not in elf:
        raise SystemExit('Unexpected ELF ABI: ' + token)
PY
fi
printf 'Evidence: %s\nCompiler/modpost exit: %s\n' "$run_dir" "$build_rc"
exit "$build_rc"
