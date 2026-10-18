import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "initramfs_audit", ROOT / "tools/audit-initramfs.py")
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class CpioAuditTests(unittest.TestCase):
    def test_scan_newc_find_required_openwrt_init_files(self):
        raw = Path("/home/hermes/sbg3300-openwrt/test_port/openwrt/build_dir/target-mips_mips32_musl/linux-bmips_bcm63268/vmlinux-initramfs").read_bytes()
        archive = mod.extract_newc(raw)
        audit = mod.audit_entries(archive)
        self.assertEqual(audit["initramfs_format"], "newc")
        self.assertIn("init", audit["required_paths"])
        self.assertIn("sbin/init", audit["required_paths"])
        self.assertIn("bin/busybox", audit["required_paths"])
        self.assertIn("etc/preinit", audit["required_paths"])
        self.assertIn("sbin/procd", audit["required_paths"])
        self.assertTrue(audit["has_trailer"])

    def test_rejects_truncated_newc(self):
        with self.assertRaises(ValueError):
            mod.extract_newc(b"070701" + b"0" * 20)


if __name__ == "__main__":
    unittest.main()