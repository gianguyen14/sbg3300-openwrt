# SPDX-License-Identifier: GPL-2.0-only
"""Exercise the actual shell fragment checker without invoking a kernel build."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


class CoverageTests(unittest.TestCase):
    def check(self, config):
        script = (Path(__file__).resolve().parents[1] /
                  "tools/build-pre-final-kernel.sh").read_text()
        start = script.index("while IFS= read -r setting; do")
        end = script.index("\nrg -q", start)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "coverage.fragment").write_text(
                "CONFIG_BCMA_HOST_SOC=y\n# CONFIG_BCMA_SFLASH is not set\n")
            (root / ".config").write_text(config)
            env = os.environ.copy()
            env.update(kernel=str(root), run_dir=str(root))
            return subprocess.run(["bash", "-c", "set -e\n" + script[start:end]],
                                  env=env, text=True, capture_output=True)

    def test_explicit_enable_and_disable_survive(self):
        result = self.check("CONFIG_BCMA_HOST_SOC=y\n# CONFIG_BCMA_SFLASH is not set\n")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_unrequested_serial_flash_rejected(self):
        result = self.check("CONFIG_BCMA_HOST_SOC=y\nCONFIG_BCMA_SFLASH=y\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Missing requested setting: # CONFIG_BCMA_SFLASH is not set", result.stderr)

    def test_dropped_host_rejected(self):
        result = self.check("# CONFIG_BCMA_HOST_SOC is not set\n# CONFIG_BCMA_SFLASH is not set\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Missing requested setting: CONFIG_BCMA_HOST_SOC=y", result.stderr)


if __name__ == "__main__":
    unittest.main()
