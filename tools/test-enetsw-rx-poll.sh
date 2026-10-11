#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-or-later
set -euo pipefail
project_dir="$(cd "$(dirname "$0")/.." && pwd)"
source_file="${ENETSW_SOURCE:?Set ENETSW_SOURCE to the actual prepared kernel C file}"
evidence_root="${ENETSW_TEST_ROOT:-$HOME/.cache/sbg3300-enetsw-rx-tests}"
mkdir -p "$evidence_root"
run_dir="$(mktemp -d "$evidence_root/run-XXXXXX")"
sha256sum "$source_file" > "$run_dir/source.sha256"
python3 "$project_dir/tools/extract-enetsw-rx-poll-test.py" \
  "$source_file" "$run_dir/enetsw-rx-poll-under-test.inc"
"${CC:-cc}" -std=c11 -Wall -Wextra -Werror ${ENET_TEST_CFLAGS:-} \
  -I"$run_dir" "$project_dir/tests/test_enetsw_rx_poll.c" -o "$run_dir/test-enetsw"
if [[ -n "${ENET_TEST_EMULATOR:-}" ]]; then
  "$ENET_TEST_EMULATOR" "$run_dir/test-enetsw" > "$run_dir/result.log" 2>&1
else
  "$run_dir/test-enetsw" > "$run_dir/result.log" 2>&1
fi
cat "$run_dir/result.log"
printf 'Evidence: %s\n' "$run_dir"
