#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
# Execute upstream OOB callbacks against public legacy geometry facts, CPU-only.
set -euo pipefail
project_dir="$(cd "$(dirname "$0")/.." && pwd)"
source_file="${BRCMNAND_SOURCE:?Set BRCMNAND_SOURCE to the pinned real driver C file}"
evidence_root="${NAND_TEST_ROOT:-$HOME/.cache/sbg3300-nand-oob-tests}"
mkdir -p "$evidence_root"
run_dir="$(mktemp -d "$evidence_root/run-XXXXXX")"
python3 - "$source_file" "$run_dir/brcmnand-oob-under-test.inc" <<'PY'
from pathlib import Path
import sys
s=Path(sys.argv[1]).read_text(); pieces=[]
for name in ('ecc','free'):
 start=s.index('static int brcmnand_hamming_ooblayout_'+name+'(')
 end=s.index('\n}',start)+2
 pieces.append(s[start:end])
Path(sys.argv[2]).write_text('\n\n'.join(pieces)+'\n')
PY
sha256sum "$source_file" > "$run_dir/source.sha256"
"${CC:-cc}" -std=c11 -Wall -Wextra -Werror ${NAND_TEST_CFLAGS:-} \
  -I"$run_dir" "$project_dir/tests/test_brcmnand_oob.c" -o "$run_dir/test-oob"
if [[ -n "${NAND_TEST_EMULATOR:-}" ]]; then
  "$NAND_TEST_EMULATOR" "$run_dir/test-oob" > "$run_dir/result.log" 2>&1
else
  "$run_dir/test-oob" > "$run_dir/result.log" 2>&1
fi
cat "$run_dir/result.log"
printf 'Evidence: %s\n' "$run_dir"
