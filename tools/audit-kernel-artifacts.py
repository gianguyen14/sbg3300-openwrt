#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Inspect regular offline ELF files; never access a device or certify an image."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

VERMAGIC = "6.18.54 SMP mod_unload BMIPS 32BIT"


class ArtifactError(ValueError):
    pass


def span(data, offset, size):
    if offset < 0 or size < 0 or offset + size > len(data):
        raise ArtifactError("truncated ELF range")
    return data[offset:offset + size]


def string(data, offset):
    if offset < 0 or offset >= len(data):
        raise ArtifactError("invalid ELF string offset")
    end = data.find(b"\0", offset)
    if end < 0:
        raise ArtifactError("unterminated ELF string")
    return data[offset:end].decode("ascii", errors="strict")


def inspect_elf(data, module=False, loader=False):
    if span(data, 0, 7) != b"\x7fELF\x01\x02\x01":
        raise ArtifactError("requires ELF32 big-endian version 1")
    header = struct.unpack(">HHIIIIIHHHHHH", span(data, 16, 36))
    kind, machine, version, entry, phoff, shoff, flags, ehsize, phsize, phnum, shsize, shnum, shstr = header
    if machine != 8 or version != 1 or ehsize != 52:
        raise ArtifactError("requires MIPS ELF version 1 header")
    if loader:
        if module or flags != 0:
            raise ArtifactError("loader inspection requires the explicit ABI-unspecified executable")
    elif flags & 0xf000 != 0x1000:
        raise ArtifactError("requires explicit MIPS/o32 ELF header")
    if kind != (1 if module else 2):
        raise ArtifactError("unexpected ELF type")
    segments = []
    if phnum:
        if phsize != 32:
            raise ArtifactError("invalid program header table")
        for i in range(phnum):
            ptype, offset, vaddr, paddr, filesz, memsz, pflags, align = struct.unpack(
                ">IIIIIIII", span(data, phoff + i * 32, 32))
            if ptype == 1:  # PT_LOAD
                if (filesz > memsz or vaddr + memsz > 2 ** 32 or
                        paddr + memsz > 2 ** 32):
                    raise ArtifactError("invalid load segment")
                if align > 1 and (align & (align - 1) or offset % align != vaddr % align):
                    raise ArtifactError("invalid load segment alignment")
                span(data, offset, filesz)
                if loader and memsz:
                    for prior in segments:
                        for key, start in (("virtual_address", vaddr), ("physical_address", paddr)):
                            if (start < prior[key] + prior["memory_bytes"] and
                                    prior[key] < start + memsz):
                                raise ArtifactError("overlapping loader memory ranges")
                segments.append({"virtual_address": vaddr, "physical_address": paddr,
                                 "file_offset": offset, "alignment": align,
                                 "file_bytes": filesz, "memory_bytes": memsz, "flags": pflags})
    if loader and not any(s["flags"] & 1 and s["virtual_address"] <= entry <
                          s["virtual_address"] + s["file_bytes"] for s in segments):
        raise ArtifactError("loader entry outside executable load segments")
    sections = []
    if shnum:
        if shsize != 40 or shstr >= shnum:
            raise ArtifactError("invalid section table")
        sections = [struct.unpack(">IIIIIIIIII", span(data, shoff + i * 40, 40))
                    for i in range(shnum)]
        names = span(data, sections[shstr][4], sections[shstr][5])
    else:
        names = b""
    metadata = {}
    imports = set()
    has_symbols = False
    for section in sections:
        name = string(names, section[0])
        if name == ".modinfo":
            for field in span(data, section[4], section[5]).split(b"\0"):
                if b"=" in field:
                    key, value = field.decode("ascii").split("=", 1)
                    metadata.setdefault(key, []).append(value.strip())
        if section[1] != 2:  # SHT_SYMTAB
            continue
        has_symbols = True
        if section[9] != 16 or section[5] % 16 or section[6] >= len(sections):
            raise ArtifactError("invalid symbol table")
        strings_section = sections[section[6]]
        strings = span(data, strings_section[4], strings_section[5])
        symbols = span(data, section[4], section[5])
        for offset in range(0, len(symbols), 16):
            stname, _, _, info, _, index = struct.unpack(">IIIBBH", symbols[offset:offset + 16])
            if index == 0 and info >> 4 in (1, 2) and stname:
                imports.add(string(strings, stname))
    if module and metadata.get("vermagic") != [VERMAGIC]:
        raise ArtifactError("unexpected or missing module vermagic")
    if module and not has_symbols:
        raise ArtifactError("module symbol table required to audit dependencies")
    return {"elf": "ELF32-MIPS-BE-ABI-unspecified" if loader else "ELF32-MIPS-BE-o32",
            "type": "module" if module else "loader" if loader else "executable",
            "entry": entry, "segments": segments, "modinfo": metadata,
            "imports": sorted(imports)}


def audit_file(path, exports=None, expected_sha=None, loader=False):
    if not path.is_file():
        raise ArtifactError("input must be an existing regular file")
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if expected_sha is not None and digest != expected_sha:
        raise ArtifactError("artifact SHA256 mismatch")
    result = inspect_elf(data, module=path.suffix == ".ko", loader=loader)
    if path.suffix == ".ko":
        if exports is None:
            raise ArtifactError("module audit requires matching Module.symvers")
        missing = sorted(set(result["imports"]) - exports)
        if missing:
            raise ArtifactError("unresolved module imports: " + ", ".join(missing))
        result["missing_imports"] = missing
    result.update({"name": path.name, "bytes": len(data), "sha256": digest,
                   "runtime": "NOT-TESTED", "image_safety": "NOT-FLASHABLE"})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symvers", type=Path)
    parser.add_argument("--loader", action="store_true",
                        help="Inspect an ABI-unspecified offline loader; never a module")
    parser.add_argument("files", type=Path, nargs="+")
    args = parser.parse_args()
    exports = None
    if args.symvers:
        if not args.symvers.is_file():
            raise ArtifactError("Module.symvers must be a regular file")
        exports = {line.split()[1] for line in args.symvers.read_text().splitlines()}
    results = [audit_file(path, exports, loader=args.loader) for path in args.files]
    print(json.dumps({"scope": "OFFLINE-ONLY", "artifacts": results}, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ArtifactError, UnicodeError, OSError, IndexError) as exc:
        print("Artifact audit failed: " + str(exc), file=sys.stderr)
        raise SystemExit(1)
