#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
set -euo pipefail
project_dir="$(cd "$(dirname "$0")/.." && pwd)"
test_dir="$(mktemp -d)"
trap 'rm -rf "$test_dir"' EXIT
"${CC:-cc}" -std=c11 -Wall -Wextra -Werror ${XTM_TEST_CFLAGS:-} \
  "$project_dir/drivers/xtm/xtm_core.c" \
  "$project_dir/tests/test_xtm_core.c" -o "$test_dir/test-xtm-core"
"$test_dir/test-xtm-core"
