#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
set -euo pipefail
project_dir="$(cd "$(dirname "$0")/.." && pwd)"
openwrt_dir="${OPENWRT_DIR:?Set OPENWRT_DIR to the reviewed patched source checkout}"
kernel_dir="${KERNEL_DIR:?Set KERNEL_DIR to the preserved Linux 6.18.54 tree}"
schema_bin="${DT_SCHEMA_BIN:?Set DT_SCHEMA_BIN to the isolated dtschema bin directory}"
evidence_root="${DTS_BUILD_ROOT:-$HOME/.cache/sbg3300-offline-dts}"
test -x "$kernel_dir/scripts/dtc/dtc"
test -x "$schema_bin/dt-validate"
mkdir -p "$evidence_root"
run_dir="$(mktemp -d "$evidence_root/run-XXXXXX")"
mkdir -p "$run_dir/schema-tree/Documentation/devicetree"
cp -a --reflink=auto "$kernel_dir/Documentation/devicetree/bindings" \
  "$run_dir/schema-tree/Documentation/devicetree/"
# Apply reviewed schema deltas to the private validation copy, not the kernel.
for patch in 0001-brcm-sbg3300-compatible.patch 0002-bcm63268-resource-bindings.patch; do
  patch -d "$run_dir/schema-tree" -p1 --batch --forward --dry-run \
    < "$project_dir/integration/schema-patches/$patch" > "$run_dir/$patch.dry-run.log"
  patch -d "$run_dir/schema-tree" -p1 --batch --forward \
    < "$project_dir/integration/schema-patches/$patch" > "$run_dir/$patch.apply.log"
done
bindings="$run_dir/schema-tree/Documentation/devicetree/bindings"
cp "$project_dir/integration/bindings/net/brcm,bcm63268-xtm-dma.yaml" "$bindings/net/"
cc -E -nostdinc -undef -D__DTS__ -x assembler-with-cpp \
  -I "$openwrt_dir/target/linux/bmips/dts" -I "$kernel_dir/include" \
  "$project_dir/integration/dts/sbg3300-sar-resources-OFFLINE-ONLY.dts" \
  > "$run_dir/source.dts"
"$kernel_dir/scripts/dtc/dtc" -I dts -O dtb -o "$run_dir/board.dtb" \
  "$run_dir/source.dts" 2> "$run_dir/dtc.log"
"$kernel_dir/scripts/dtc/dtc" -I dtb -O dts -o "$run_dir/roundtrip.dts" \
  "$run_dir/board.dtb" 2>> "$run_dir/dtc.log"
"$schema_bin/python" "$project_dir/tools/check-offline-dtb.py" "$run_dir/board.dtb" \
  > "$run_dir/contract.json"
"$schema_bin/dt-doc-validate" "$bindings/mips/brcm/soc.yaml" \
  "$bindings/mfd/brcm,bcm63268-gpio-sysctl.yaml" \
  "$bindings/phy/brcm,bcm63xx-usbh-phy.yaml" "$bindings/rng/brcm,bcm2835.yaml" \
  "$bindings/net/brcm,bcm63268-enetsw.yaml" "$bindings/net/brcm,bcm63268-xtm-dma.yaml" \
  "$bindings/pci/brcm,bcm6328-pcie.yaml" > "$run_dir/meta-schema.log" 2>&1
"$schema_bin/dt-mk-schema" -j "$bindings" > "$run_dir/schemas.json" 2> "$run_dir/schema-build.log"
"$schema_bin/dt-validate" -s "$run_dir/schemas.json" "$run_dir/board.dtb" \
  > "$run_dir/full-board-schema.log" 2>&1
# Some dt-schema releases print errors but exit zero. Require empty diagnostics.
for log in dtc.log meta-schema.log schema-build.log full-board-schema.log; do
  if [[ -s "$run_dir/$log" ]]; then
    printf 'Validation diagnostics remain: %s\n' "$run_dir/$log" >&2
    exit 1
  fi
done
sha256sum "$run_dir/board.dtb" > "$run_dir/board.sha256"
printf 'Offline DTS/schema contract validated. Evidence: %s\n' "$run_dir"
