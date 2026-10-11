# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
import re
import unittest


class Sbg3300PatchContractTests(unittest.TestCase):
    def _read_patch(self) -> str:
        return (Path(__file__).resolve().parents[1] /
                "patches/openwrt/0012-bmips-sbg3300-add-gpio-leds.patch").read_text()

    def test_gpio_keys_use_gpio_controller_phandles(self):
        patch = self._read_patch()
        self.assertNotIn("ext_irq", patch)
        self.assertIn("gpios = <&gpio 1 GPIO_ACTIVE_LOW>;", patch)
        self.assertIn("gpios = <&gpio 0 GPIO_ACTIVE_LOW>;", patch)

    def test_gpio_leds_only_include_direct_gpio_lines(self):
        patch = self._read_patch()
        self.assertIn("gpios = <&gpio 20 GPIO_ACTIVE_LOW>;", patch)
        self.assertIn("gpios = <&gpio 21 GPIO_ACTIVE_LOW>;", patch)
        self.assertIn("gpios = <&gpio 14 GPIO_ACTIVE_LOW>;", patch)
        self.assertIn("gpios = <&gpio 15 GPIO_ACTIVE_LOW>;", patch)
        self.assertIn("gpios = <&gpio 22 GPIO_ACTIVE_HIGH>;", patch)
        self.assertIn("gpios = <&gpio 8 GPIO_ACTIVE_LOW>;", patch)
        self.assertNotIn("gpios = <&gpio 2 GPIO_ACTIVE_LOW>;", patch)
        self.assertNotIn("gpios = <&gpio 6 GPIO_ACTIVE_LOW>;", patch)
        self.assertNotIn("gpios = <&gpio 5 GPIO_ACTIVE_LOW>;", patch)

    def test_patch_hunk_header_line_count_matches_content(self):
        patch = self._read_patch()
        hunk_header = re.search(r"^@@ -\d+,\d+ \+\d+,(\d+) @@", patch, re.MULTILINE)
        self.assertIsNotNone(hunk_header)
        expected_new_lines = int(hunk_header.group(1))
        hunk_body = patch.split(hunk_header.group(0), 1)[1]
        hunk_lines = []
        for line in hunk_body.splitlines():
            if line.startswith(("-- ", "diff --git ")):
                break
            if line.startswith(("+", " ", "-")):
                hunk_lines.append(line)
        actual_new_lines = sum(
            1 for line in hunk_lines if line.startswith(("+", " "))
        )
        self.assertEqual(expected_new_lines, actual_new_lines)


if __name__ == "__main__":
    unittest.main()
