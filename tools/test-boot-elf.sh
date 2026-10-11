#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
# Synthetic userspace ELF fixture only; no kernel payload or device operation.
set -euo pipefail
project_dir="$(cd "$(dirname "$0")/.." && pwd)"
openwrt_dir="${OPENWRT_DIR:-$HOME/sbg3300-openwrt-source}"
cross="$openwrt_dir/staging_dir/toolchain-mips_mips32_gcc-14.4.0_musl/bin/mips-openwrt-linux-musl-"
export STAGING_DIR="$openwrt_dir/staging_dir/target-mips_mips32_musl"
evidence_root="${BOOT_TEST_ROOT:-$HOME/.cache/sbg3300-boot-elf-tests}"
mkdir -p "$evidence_root"
run_dir="$(mktemp -d "$evidence_root/run-XXXXXX")"
cat > "$run_dir/exit.S" <<'ASM'
/* SPDX-License-Identifier: GPL-2.0-only */
.set noreorder
.text
.globl startup
.ent startup
startup:
 li $v0, 4001
 li $a0, 0
 syscall
 nop
.end startup
ASM
"${cross}gcc" -mabi=32 -mips32 -mno-abicalls -fno-pic -c \
  "$run_dir/exit.S" -o "$run_dir/exit.o" > "$run_dir/compiler.log" 2>&1
"${cross}ld" -e startup -Ttext 0x00410000 "$run_dir/exit.o" \
  -o "$run_dir/explicit-o32.elf" >> "$run_dir/compiler.log" 2>&1
python3 "$project_dir/tools/audit-kernel-artifacts.py" \
  --loader "$run_dir/explicit-o32.elf" > "$run_dir/explicit-audit.json"
"${QEMU_MIPS:-qemu-mips-static}" "$run_dir/explicit-o32.elf" \
  > "$run_dir/explicit-qemu.log" 2>&1
# Model the pinned loader's binary -> relocatable-data -> ELF wrapper pipeline.
"${cross}objcopy" -O binary -R .reginfo -R .MIPS.abiflags -S \
  "$run_dir/explicit-o32.elf" "$run_dir/payload.bin"
(cd "$run_dir"; "${cross}ld" -r -b binary --oformat elf32-tradbigmips \
  payload.bin -o wrapped.o) >> "$run_dir/compiler.log" 2>&1
cat > "$run_dir/wrapper.lds" <<'LDS'
/* SPDX-License-Identifier: GPL-2.0-only */
OUTPUT_ARCH(mips)
SECTIONS { .text : { startup = .; *(.data) } }
LDS
"${cross}ld" -e startup -T "$run_dir/wrapper.lds" -Ttext 0x00410000 \
  "$run_dir/wrapped.o" -o "$run_dir/wrapped-OFFLINE-ONLY.elf" \
  >> "$run_dir/compiler.log" 2>&1
set +e
python3 "$project_dir/tools/audit-kernel-artifacts.py" --loader \
  "$run_dir/wrapped-OFFLINE-ONLY.elf" > "$run_dir/wrapped-audit.log" 2>&1
result=$?
set -e
printf '%s\n' "$result" > "$run_dir/wrapped-audit.exit"
(( result == 1 )) || { printf 'Expected strict wrapper rejection: %s\n' "$run_dir" >&2; exit 1; }
"${cross}readelf" -h -l "$run_dir/wrapped-OFFLINE-ONLY.elf" \
  > "$run_dir/wrapped-readelf.log"
sha256sum "$run_dir/"*.elf > "$run_dir/artifacts.sha256"
printf 'Synthetic ELF compiler/QEMU and wrapper rejection PASS: %s\n' "$run_dir"
