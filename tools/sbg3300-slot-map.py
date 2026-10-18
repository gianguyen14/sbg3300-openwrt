#!/usr/bin/env python3
"""Offline arithmetic audit for Broadcom/MSTC NAND image-tag addresses.

No device access and no image writing. This computes the inspected family-BSP
address expression; it does not prove a specific stock kernel build used it.
"""
from dataclasses import dataclass
from pathlib import Path

TAG_BLOCK_LEN = 0x20000
IMAGE_BASE = 0xBFC00000
FLASH_BASE = 0xB8000000
# Keep this explicitly 32-bit: MIPS kernel headers compute unsigned address
# arithmetic modulo 2^32. A Python negative offset is not the hardware result.
ADDRESS_MASK = 0xFFFFFFFF
BOOT_OFFSET = (FLASH_BASE - IMAGE_BASE) & ADDRESS_MASK


@dataclass(frozen=True)
class StockTag:
    rootfs_address: int
    rootfs_length: int
    total_length: int


def _ascii_decimal(data: bytes, offset: int, width: int, field: str) -> int:
    raw = data[offset:offset + width].split(b"\0", 1)[0]
    if not raw or not raw.isdigit():
        raise ValueError(f"invalid ASCII decimal {field} at 0x{offset:x}")
    return int(raw, 10)


def read_stock_tag(path: Path) -> StockTag:
    data = Path(path).read_bytes()
    if len(data) < 0x20000:
        raise ValueError("stock image shorter than 128 KiB tag block")
    if data[0:1] != b"6" or data[4:8] != b"MSTC":
        raise ValueError("not an MSTC tag-v6 image")
    return StockTag(
        rootfs_address=_ascii_decimal(data, 0x5e, 12, "rootfsAddress"),
        rootfs_length=_ascii_decimal(data, 0x6a, 10, "rootfsLen"),
        total_length=_ascii_decimal(data, 0x3e, 10, "totalImageLen"),
    )


def vendor_rootfs_offset(rootfs_address: int) -> int:
    """Family BSP bcm63xx-nand.c formula: addr + BOOT_OFFSET - FLASH_BASE."""
    offset = (rootfs_address + BOOT_OFFSET - FLASH_BASE) & ADDRESS_MASK
    if offset > 0x08000000:
        raise ValueError("translated rootfs address exceeds observed 128MiB chip")
    return offset


def vendor_slot2_write_offset(total_flash_size: int) -> int:
    if total_flash_size <= 0 or total_flash_size % 2:
        raise ValueError("flash size must be positive and even")
    return total_flash_size // 2 + TAG_BLOCK_LEN


def live_rootfs_extent(offset: int, size: int) -> tuple[int, int]:
    if offset < 0 or size <= 0:
        raise ValueError("invalid MTD extent")
    return offset, offset + size
