#!/usr/bin/env python3
"""Read-only checks for an ELF carrying a built-in Linux initramfs.

This tool only parses CPIO newc records embedded in a kernel artifact. It does
not execute the kernel, emulate CFE, mount a filesystem or access hardware.
"""
from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

MAGIC = (b"070701", b"070702")
HEADER_SIZE = 110
REQUIRED = ("init", "sbin/init", "bin/busybox", "etc/preinit", "sbin/procd")


def _hex8(raw: bytes) -> int:
    if len(raw) != 8:
        raise ValueError("short newc header field")
    try:
        return int(raw, 16)
    except ValueError as exc:
        raise ValueError("invalid newc hex field") from exc


# Locate the first plausible aligned newc archive: cpio ASCII magic begins
# at a 4-byte boundary, but may occur in the kernel's string table too. We
# select the first candidate whose records parse fully through TRAILER!!!.

def extract_newc(blob: bytes) -> list[dict]:
    candidates = []
    for magic in MAGIC:
        pos = blob.find(magic)
        while pos >= 0:
            if pos % 4 == 0:
                candidates.append(pos)
            pos = blob.find(magic, pos + 1)
    for start in sorted(set(candidates)):
        try:
            return _parse_newc_at(blob, start)
        except ValueError:
            continue
    raise ValueError("complete newc archive not found")


def _parse_newc_at(blob: bytes, pos: int) -> list[dict]:
    entries = []
    while True:
        if pos + HEADER_SIZE > len(blob):
            raise ValueError("truncated newc header")
        magic = blob[pos:pos + 6]
        if magic not in MAGIC:
            raise ValueError(f"bad newc magic at offset 0x{pos:x}")
        fields = []
        for i in range(13):
            fields.append(_hex8(blob[pos + 6 + i * 8:pos + 14 + i * 8]))
        mode, filesize, namesize = fields[1], fields[6], fields[11]
        if namesize < 1:
            raise ValueError("invalid newc name length")
        name_start = pos + HEADER_SIZE
        name_end = name_start + namesize
        if name_end > len(blob):
            raise ValueError("truncated newc name")
        name_bytes = blob[name_start:name_end]
        if name_bytes[-1:] != b"\0":
            raise ValueError("newc name lacks NUL terminator")
        name = name_bytes[:-1].decode("utf-8", "replace")
        data_start = (name_end + 3) & ~3
        data_end = data_start + filesize
        if data_end > len(blob):
            raise ValueError(f"truncated newc data for {name!r}")
        entries.append({"name": name, "mode": mode, "size": filesize,
                        "data_offset": data_start})
        if name == "TRAILER!!!":
            return entries
        pos = (data_end + 3) & ~3
        # The archive starts in a raw kernel blob and may be followed by
        # alignment/padding. Stop at the first non-newc record after trailer.
        # (Trailer normally returns above.)
    raise ValueError("newc archive trailer not found")


def audit_entries(entries: list[dict]) -> dict:
    names = {item["name"] for item in entries}
    missing = [name for name in REQUIRED if name not in names]
    return {
        "initramfs_format": "newc",
        "record_count_including_trailer": len(entries),
        "has_trailer": bool(entries and entries[-1]["name"] == "TRAILER!!!"),
        "required_paths": {name: name in names for name in REQUIRED},
        "missing_required_paths": missing,
        "embedded_initramfs_content_present": not missing,
        "scope": "static file parsing only; no kernel/CFE boot tested",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()
    try:
        entries = extract_newc(args.artifact.read_bytes())
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    result = audit_entries(entries)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["embedded_initramfs_content_present"] and result["has_trailer"] else 1


if __name__ == "__main__":
    raise SystemExit(main())