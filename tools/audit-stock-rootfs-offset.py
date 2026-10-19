#!/usr/bin/env python3
"""Read-only audit of stock Broadcom tag fields and vendor BSP offset math.

No device access. This reports source-family arithmetic only; it cannot prove
that the 2018 stock kernel used this exact source or that the image booted.
"""
import argparse
import hashlib
import json
from pathlib import Path

IMAGE_BASE = 0xBFC00000
FLASH_BASE = 0xB8000000
ADDRESS_MASK = 0xFFFFFFFF
BOOT_OFFSET = (FLASH_BASE - IMAGE_BASE) & ADDRESS_MASK
TAG_BLOCK = 0x20000
LIVE_ROOTFS_OFFSET = 0x04020000


def dec_field(data: bytes, off: int, width: int, name: str) -> int:
    raw = data[off:off + width].split(b"\0", 1)[0]
    if not raw or not raw.isdigit():
        raise ValueError(f"invalid decimal tag field {name} at +0x{off:x}")
    return int(raw, 10)


def audit_stock(path: Path) -> dict:
    data = path.read_bytes()
    if len(data) < TAG_BLOCK:
        raise ValueError("stock file shorter than 128KiB tag area")
    if data[:1] != b"6" or data[4:8] != b"MSTC":
        raise ValueError("not an MSTC tag-v6 image")
    root_addr = dec_field(data, 0x5e, 12, "rootfsAddress")
    root_len = dec_field(data, 0x6a, 10, "rootfsLen")
    total_len = dec_field(data, 0x3e, 10, "totalImageLen")
    slot1_offset = (root_addr + BOOT_OFFSET - FLASH_BASE) & ADDRESS_MASK
    slot2_rootfs_address = (IMAGE_BASE + (0x08000000 // 2) + TAG_BLOCK) & ADDRESS_MASK
    slot2_offset = (slot2_rootfs_address + BOOT_OFFSET - FLASH_BASE) & ADDRESS_MASK
    return {
        "file": str(path),
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "tag_rootfs_address": f"0x{root_addr:08x}",
        "tag_rootfs_length": f"0x{root_len:x}",
        "tag_total_length": f"0x{total_len:x}",
        "file_payload_start": "0x20000",
        "file_payload_end": f"0x{0x20000 + total_len:x}",
        "vendor_flash_base": f"0x{FLASH_BASE:08x}",
        "vendor_boot_offset": f"0x{BOOT_OFFSET & 0xffffffff:08x}",
        "slot1_vendor_formula_offset": f"0x{slot1_offset:x}",
        "slot2_tag_rootfs_address_from_family_inactive_slot_rule": f"0x{slot2_rootfs_address:08x}",
        "slot2_vendor_formula_offset": f"0x{slot2_offset:x}",
        "live_rootfs_offset_from_sanitized_dmesg": f"0x{LIVE_ROOTFS_OFFSET:x}",
        "slot1_offset_delta_from_live": f"0x{slot1_offset - LIVE_ROOTFS_OFFSET:x}",
        "slot2_offset_delta_from_live": f"0x{slot2_offset - LIVE_ROOTFS_OFFSET:x}",
        "source_equivalence": "NOT_PROVEN: family BSP mirror is not verified as the exact 2018 running kernel source/build",
        "interpretation": "stock image tag address translates to slot 1; family updater's inactive-slot formula maps slot 2 to live MTD start, consistent with but not proof of active slot 2",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stock_image", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(audit_stock(args.stock_image), indent=2, sort_keys=True))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())