# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
import unittest


class Sbg3300PatchContractTests(unittest.TestCase):
    def test_gpio_keys_use_gpio_controller_phandles(self):
        patch = (Path(__file__).resolve().parents[1] /
                 "patches/openwrt/0012-bmips-sbg3300-add-gpio-leds.patch").read_text()
        self.assertNotIn("ext_irq", patch)
        self.assertIn("gpios = <&gpio 1 GPIO_ACTIVE_LOW>;", patch)
        self.assertIn("gpios = <&gpio 0 GPIO_ACTIVE_LOW>;", patch)

    def test_gpio_leds_only_include_direct_gpio_lines(self):
        patch = (Path(__file__).resolve().parents[1] /
                 "patches/openwrt/0012-bmips-sbg3300-add-gpio-leds.patch").read_text()
        self.assertIn("gpios = <&gpio 20 GPIO_ACTIVE_LOW>;", patch)
        self.assertIn("gpios = <&gpio 21 GPIO_ACTIVE_LOW>;", patch)
        self.assertIn("gpios = <&gpio 14 GPIO_ACTIVE_LOW>;", patch)
        self.assertIn("gpios = <&gpio 15 GPIO_ACTIVE_LOW>;", patch)
        self.assertIn("gpios = <&gpio 22 GPIO_ACTIVE_HIGH>;", patch)
        self.assertIn("gpios = <&gpio 8 GPIO_ACTIVE_LOW>;", patch)
        self.assertNotIn("gpios = <&gpio 2 GPIO_ACTIVE_LOW>;", patch)
        self.assertNotIn("gpios = <&gpio 6 GPIO_ACTIVE_LOW>;", patch)
        self.assertNotIn("gpios = <&gpio 5 GPIO_ACTIVE_LOW>;", patch)


if __name__ == "__main__":
    unittest.main()
