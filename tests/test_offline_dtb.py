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


def ethernet_candidate_fixture():
    nodes = fixture()
    host = "/soc/spi@10001000"
    switch = host + "/switch@0"
    nodes[host] = {"compatible": b"brcm,bcm6328-hsspi\0", "status": b"disabled\0"}
    nodes[switch] = {"compatible": b"brcm,bcm53125\0", "status": b"disabled\0",
                     "reg": cells(0), "spi-max-frequency": cells(781000),
                     "spi-cpol": b"", "spi-cpha": b""}
    for port in (1, 2, 3, 4, 8):
        nodes[f"{switch}/ports/port@{port:x}"] = {"reg": cells(port)}
    nodes["/soc/ethernet@1000d800"] = {"status": b"disabled\0"}
    nodes["/soc/switch@10700000"] = {"status": b"disabled\0"}
    nodes["/soc/mdio@107000b0"] = {"status": b"disabled\0"}
    return nodes


class DtbTests(unittest.TestCase):
    def test_unverified_radio_and_gpio_consumers_remain_disabled(self):
        for compatible in (b"brcm,bus-axi\0", b"gpio-leds\0",
                           b"gpio-keys\0", b"gpio-keys-polled\0"):
            for status in (None, b"okay\0"):
                nodes = fixture()
                props = {"compatible": compatible}
                if status is not None:
                    props["status"] = status
                nodes["/unverified"] = props
                with self.assertRaises(ValueError):
                    audit.verify(nodes)
            nodes["/unverified"]["status"] = b"disabled\0"
            audit.verify(nodes)
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
                      {"compatible": b"brcm,bcm63268-enetsw\0", "status": b"okay\0"},
                      {"compatible": b"brcm,bcm53125\0", "status": b"okay\0"}]:
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

    def test_ethernet_candidate_contract(self):
        nodes = ethernet_candidate_fixture()
        self.assertEqual(
            audit.verify_ethernet_candidate(nodes)["dsa_endpoint"],
            "OMITTED-UNRESOLVED")

    def test_ethernet_candidate_rejects_unverified_activation(self):
        cases = [
            ("/soc/spi@10001000", "status", b"okay\0"),
            ("/soc/spi@10001000/switch@0", "status", b"okay\0"),
            ("/soc/spi@10001000/switch@0", "reg", cells(5)),
            ("/soc/spi@10001000/switch@0", "dsa-tag-protocol", b"dsa\0"),
            ("/soc/spi@10001000/switch@0", "ethernet", cells(1)),
            ("/soc/spi@10001000/switch@0/ports/port@1", "label", b"lan1\0"),
            ("/soc/spi@10001000/switch@0/ports/port@8", "phy-mode", b"rgmii-id\0"),
            ("/soc/spi@10001000/switch@0/ports/port@8", "reg", cells(7)),
            ("/soc/ethernet@1000d800", "status", b"okay\0"),
        ]
        for path, prop, value in cases:
            with self.subTest(path=path, prop=prop):
                nodes = ethernet_candidate_fixture()
                nodes[path][prop] = value
                with self.assertRaises(ValueError):
                    audit.verify_ethernet_candidate(nodes)

        nodes = ethernet_candidate_fixture()
        nodes["/soc/spi@10001000/switch@0/ports/port@8/fixed-link"] = {
            "speed": cells(1000), "full-duplex": b""}
        with self.assertRaises(ValueError):
            audit.verify_ethernet_candidate(nodes)

    def test_ethernet_candidate_rejects_duplicate_mdio_binding(self):
        nodes = ethernet_candidate_fixture()
        nodes["/soc/mdio@107000b0/mdio@1/switch@1e"] = {
            "compatible": b"brcm,bcm53125\0", "status": b"disabled\0"}
        with self.assertRaises(ValueError):
            audit.verify_ethernet_candidate(nodes)


if __name__ == "__main__":
    unittest.main()
