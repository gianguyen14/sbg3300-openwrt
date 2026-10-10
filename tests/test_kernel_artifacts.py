# SPDX-License-Identifier: GPL-2.0-only
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest

spec = importlib.util.spec_from_file_location(
    "artifact_audit", Path(__file__).resolve().parents[1] / "tools/audit-kernel-artifacts.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def elf(kind=2, machine=8, flags=0x50001001):
    return (b"\x7fELF\x01\x02\x01" + bytes(9) +
            struct.pack(">HHIIIIIHHHHHH", kind, machine, 1, 0, 0, 0, flags,
                        52, 0, 0, 40, 0, 0))


def module_elf(vermagic=audit.VERMAGIC, symbol="test_import"):
    names = b"\0.shstrtab\0.modinfo\0.symtab\0.strtab\0"
    metadata = ("vermagic=" + vermagic + "\0license=GPL\0name=test\0").encode()
    symbols = bytes(16) + struct.pack(">IIIBBH", 1, 0, 0, 0x10, 0, 0)
    strings = b"\0" + symbol.encode() + b"\0"
    payload = names + metadata + symbols + strings
    header = bytearray(elf(kind=1))
    struct.pack_into(">I", header, 32, 52 + len(payload))
    struct.pack_into(">H", header, 48, 5)
    struct.pack_into(">H", header, 50, 1)
    sections = bytes(40)
    offset = 52
    for name, stype, content, link, entsize in [
            (1, 3, names, 0, 0), (11, 1, metadata, 0, 0),
            (20, 2, symbols, 4, 16), (28, 3, strings, 0, 0)]:
        sections += struct.pack(">IIIIIIIIII", name, stype, 0, 0, offset,
                                len(content), link, 0, 1, entsize)
        offset += len(content)
    return bytes(header) + payload + sections


def loader_elf(segments, entry=0x81000000):
    header = bytearray(elf(flags=0))
    struct.pack_into(">I", header, 24, entry)
    struct.pack_into(">I", header, 28, 52)
    struct.pack_into(">HH", header, 42, 32, len(segments))
    offset = 52 + 32 * len(segments)
    payload = b""
    for vaddr, paddr, filesz, memsz, align in segments:
        header += struct.pack(">IIIIIIII", 1, offset + len(payload), vaddr, paddr,
                              filesz, memsz, 5, align)
        payload += bytes(filesz)
    return bytes(header) + payload


class ArtifactTests(unittest.TestCase):
    def test_executable(self):
        self.assertEqual(audit.inspect_elf(elf())["elf"], "ELF32-MIPS-BE-o32")

    def test_wrong_abi(self):
        for value in [elf(machine=62), elf(flags=0), elf(kind=1), b"", elf()[:40],
                      elf().replace(b"\x01\x02\x01", b"\x02\x01\x01", 1)]:
            with self.assertRaises(audit.ArtifactError):
                audit.inspect_elf(value)

    def test_module_requires_vermagic(self):
        with self.assertRaises(audit.ArtifactError):
            audit.inspect_elf(elf(kind=1), module=True)

    def test_module_imports_and_vermagic(self):
        self.assertEqual(audit.inspect_elf(module_elf(), module=True)["imports"], ["test_import"])
        with self.assertRaises(audit.ArtifactError):
            audit.inspect_elf(module_elf(vermagic="2.6.30"), module=True)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.ko"
            path.write_bytes(module_elf())
            for exports in [None, set()]:
                with self.assertRaises(audit.ArtifactError):
                    audit.audit_file(path, exports)
            self.assertFalse(audit.audit_file(path, {"test_import"})["missing_imports"])

    def test_loader_requires_explicit_mode_and_executable_entry(self):
        data = bytearray(elf(flags=0))
        struct.pack_into(">I", data, 24, 0x81000000)
        struct.pack_into(">I", data, 28, 52)
        struct.pack_into(">HH", data, 42, 32, 1)
        data += struct.pack(">IIIIIIII", 1, 84, 0x81000000, 0x81000000, 4, 4, 5, 4)
        data += bytes(4)
        with self.assertRaises(audit.ArtifactError):
            audit.inspect_elf(bytes(data))
        self.assertEqual(audit.inspect_elf(bytes(data), loader=True)["type"], "loader")
        struct.pack_into(">I", data, 24, 0)
        with self.assertRaises(audit.ArtifactError):
            audit.inspect_elf(bytes(data), loader=True)

    def test_loader_segment_physical_overflow_and_alignment(self):
        for segment in [(0x81000000, 0xFFFFFFFC, 4, 8, 4),
                        (0x81000000, 0x81000000, 4, 4, 3),
                        (0x81000000, 0x81000000, 4, 4, 8)]:
            with self.subTest(segment=segment):
                with self.assertRaises(audit.ArtifactError):
                    audit.inspect_elf(loader_elf([segment]), loader=True)

    def test_loader_entry_requires_file_backed_code(self):
        data = loader_elf([(0x81000000, 0x81000000, 4, 8, 4)], entry=0x81000004)
        with self.assertRaises(audit.ArtifactError):
            audit.inspect_elf(data, loader=True)

    def test_loader_rejects_virtual_and_physical_aliases(self):
        for second in [(0x81000000, 0x82000000, 4, 4, 4),
                       (0x82000000, 0x81000000, 4, 4, 4)]:
            data = loader_elf([(0x81000000, 0x81000000, 4, 4, 4), second])
            with self.assertRaises(audit.ArtifactError):
                audit.inspect_elf(data, loader=True)

    def test_negative_string_offset_is_rejected(self):
        with self.assertRaises(audit.ArtifactError):
            audit.string(b"x\0", -1)

    def test_hash_and_regular_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "vmlinux"
            path.write_bytes(elf())
            result = audit.audit_file(path)
            self.assertEqual(result["image_safety"], "NOT-FLASHABLE")
            with self.assertRaises(audit.ArtifactError):
                audit.audit_file(path, expected_sha="0" * 64)
            with self.assertRaises(audit.ArtifactError):
                audit.audit_file(Path(directory))

    def test_truncated_section_table(self):
        data = bytearray(elf())
        struct.pack_into(">I", data, 32, 52)
        struct.pack_into(">H", data, 48, 1)
        with self.assertRaises(audit.ArtifactError):
            audit.inspect_elf(bytes(data))


if __name__ == "__main__":
    unittest.main()
