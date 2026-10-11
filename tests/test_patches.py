# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
import unittest


class PatchSeriesTests(unittest.TestCase):
    def test_sbg3300_buttons_do_not_reference_missing_ext_irq(self):
        patch = (Path(__file__).resolve().parents[1] /
                 "patches/openwrt/0012-bmips-sbg3300-add-gpio-leds.patch").read_text()
        self.assertNotIn("&ext_irq", patch)
        self.assertIn("gpios = <&gpio 1 GPIO_ACTIVE_LOW>;", patch)
        self.assertIn("gpios = <&gpio 0 GPIO_ACTIVE_LOW>;", patch)


if __name__ == "__main__":
    unittest.main()
