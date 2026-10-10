# SPDX-License-Identifier: GPL-2.0-only
import copy
import importlib.util
from pathlib import Path
import struct
import unittest

spec = importlib.util.spec_from_file_location(
    "dtb_audit", Path(__file__).resolve().parents[1] / "tools/check-offline-dtb.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def cells(*values):
    return struct.pack(">" + "I" * len(values), *values)


def fixture():
    return {
        audit.SAR: {"status": b"disabled\0", "reg": cells(*audit.REGS),
                    "interrupts": cells(26, 59), "interrupt-parent": cells(4),
                    "clocks": cells(1, 9), "resets": cells(2, 3), "power-domains": cells(3, 0)},
        "/soc/clock-controller@10000004": {"phandle": cells(1)},
        "/soc/reset-controller@10000010": {"phandle": cells(2)},
        "/soc/power-controller@1000184c": {"phandle": cells(3)},
        "/soc/interrupt-controller@10000020": {"phandle": cells(4)},
        "/soc/nand-controller@10000200": {"status": b"disabled\0"},
        "/soc/nand-controller@10000200/nandcs@0": {"nand-on-flash-bbt": b""},
    }


class DtbTests(unittest.TestCase):
    def test_disabled_resource_contract(self):
        self.assertEqual(audit.verify(fixture())["sar"], "DISABLED")

    def test_wrong_sar_resources(self):
        for key, value in [("status", b"okay\0"), ("reg", cells(0, 16)),
                           ("interrupts", cells(26, 27)), ("clocks", cells(1, 8)),
                           ("interrupt-parent", cells(99))]:
            nodes = fixture()
            nodes[audit.SAR][key] = value
            with self.assertRaises(ValueError):
                audit.verify(nodes)

    def test_console_partitions_and_topology(self):
        for props in [{"bootargs": b"earlycon\0"}, {"stdout-path": b"serial0\0"}]:
            nodes = fixture()
            nodes["/chosen"] = props
            with self.assertRaises(ValueError):
                audit.verify(nodes)
        for props in [{"compatible": b"fixed-partitions\0"},
                      {"compatible": b"brcm,bcm63268-enetsw\0", "status": b"okay\0"}]:
            nodes = fixture()
            nodes["/extra"] = props
            with self.assertRaises(ValueError):
                audit.verify(nodes)

    def test_nand_geometry(self):
        nodes = copy.deepcopy(fixture())
        nodes["/soc/nand-controller@10000200/nandcs@0"]["nand-ecc-strength"] = cells(1)
        with self.assertRaises(ValueError):
            audit.verify(nodes)

    def test_usb_requires_phy_provider(self):
        nodes = fixture()
        nodes["/soc/usb@10002500"] = {"status": b"okay\0"}
        with self.assertRaises(ValueError):
            audit.verify(nodes)
        nodes["/soc/usb-phy@10002700"] = {"status": b"okay\0"}
        self.assertEqual(audit.verify(nodes)["sar"], "DISABLED")


if __name__ == "__main__":
    unittest.main()
