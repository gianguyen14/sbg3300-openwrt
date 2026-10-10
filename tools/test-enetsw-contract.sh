#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-or-later
set -euo pipefail
project_dir="$(cd "$(dirname "$0")/.." && pwd)"
test_dir="$(mktemp -d)"
trap 'rm -rf "$test_dir"' EXIT
"${CC:-cc}" -std=c11 -Wall -Wextra -Werror ${ENET_TEST_CFLAGS:-} \
  "$project_dir/tests/test_enetsw_contract.c" -o "$test_dir/test-enetsw"
"$test_dir/test-enetsw"
