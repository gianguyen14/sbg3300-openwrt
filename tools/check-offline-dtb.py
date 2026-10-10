#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Validate conservative SBG3300 DTB contracts, never runtime hardware support."""
import argparse
import json
from pathlib import Path
import struct
import sys

SAR = "/soc/xtm-dma@1000c000"
REGS = [0x1000c000, 4, 0x1000c200, 16, 0x1000c400, 16,
        0x1000c240, 16, 0x1000c440, 16]


def cells(data):
    if len(data) % 4:
        raise ValueError("invalid DT cell length")
    return list(struct.unpack(">" + "I" * (len(data) // 4), data))


def verify(nodes, require_sar=True):
    chosen = nodes.get("/chosen", {})
    if chosen.get("stdout-path", b"").rstrip(b"\0"):
        raise ValueError("unexpected selected console")
    args = chosen.get("bootargs", b"")
    if b"console=" in args or b"earlycon" in args:
        raise ValueError("unexpected console boot argument")
    for path, props in nodes.items():
        if b"fixed-partitions" in props.get("compatible", b"").split(b"\0"):
            raise ValueError("unapproved fixed partition map")
        if any(name in props for name in ("mac-address", "local-mac-address", "calibration-data")):
            raise ValueError("device-specific data in DTB")
        compatibles = props.get("compatible", b"").split(b"\0")
        if any(c in compatibles for c in (b"brcm,bcm63268-enetsw",
                                         b"brcm,bcm63268-switch",
                                         b"brcm,bcm53125")):
            if props.get("status") != b"disabled\0":
                raise ValueError("unverified Ethernet topology activated")
    for path in ("/soc/usb@10002500", "/soc/usb@10002600"):
        if nodes.get(path, {}).get("status") == b"okay\0":
            if nodes.get("/soc/usb-phy@10002700", {}).get("status") != b"okay\0":
                raise ValueError("enabled USB HCD references a disabled PHY")
    sar = nodes.get(SAR)
    if require_sar and (sar is None or sar.get("status") != b"disabled\0"):
        raise ValueError("SAR contract fixture missing or active")
    if sar is not None:
        if sar.get("status") != b"disabled\0":
            raise ValueError("SAR node must remain disabled")
        if cells(sar["reg"]) != REGS or cells(sar["interrupts"]) != [26, 59]:
            raise ValueError("incorrect exact-family SAR DMA resources")
        for prop, provider, index in [
                ("clocks", "/soc/clock-controller@10000004", 9),
                ("resets", "/soc/reset-controller@10000010", 3),
                ("power-domains", "/soc/power-controller@1000184c", 0)]:
            phandle = cells(nodes[provider]["phandle"])[0]
            if cells(sar[prop]) != [phandle, index]:
                raise ValueError("incorrect SAR " + prop + " provider/index")
        intc = cells(nodes["/soc/interrupt-controller@10000020"]["phandle"])[0]
        if cells(sar["interrupt-parent"]) != [intc]:
            raise ValueError("incorrect SAR IRQ domain")
    if nodes["/soc/nand-controller@10000200"].get("status") != b"disabled\0":
        raise ValueError("unverified NAND controller configuration activated")
    nand = nodes["/soc/nand-controller@10000200/nandcs@0"]
    if any(key in nand for key in ("nand-ecc-step-size", "nand-ecc-strength",
                                   "brcm,nand-oob-sector-size")):
        raise ValueError("unverified ECC/OOB override remains")
    if "nand-on-flash-bbt" not in nand:
        raise ValueError("missing retained on-flash BBT contract")
    return {"sar": "DISABLED" if sar is not None else "NOT-IN-FIXTURE",
            "topology": "UNRESOLVED-DISABLED",
            "nand": "DISABLED-UNRESOLVED-ECC-OOB", "console": "UNSELECTED",
            "runtime": "NOT-TESTED", "image_safety": "NOT-FLASHABLE"}


def verify_ethernet_candidate(nodes):
    """Check that evidence-only Ethernet candidates stay non-deployable."""
    hsspi_path = "/soc/spi@10001000"
    switch_path = hsspi_path + "/switch@0"
    hsspi = nodes.get(hsspi_path, {})
    switch = nodes.get(switch_path, {})

    if hsspi.get("status") != b"disabled\0":
        raise ValueError("candidate HSSPI controller must remain disabled")
    if b"brcm,bcm6328-hsspi" not in hsspi.get("compatible", b"").split(b"\0"):
        raise ValueError("candidate HSSPI controller is missing")
    if switch.get("status") != b"disabled\0":
        raise ValueError("candidate BCM53125 must remain disabled")
    if switch.get("compatible") != b"brcm,bcm53125\0":
        raise ValueError("candidate must contain exactly one BCM53125")
    allowed_switch_props = {
        "compatible", "reg", "spi-max-frequency", "spi-cpol", "spi-cpha",
        "status",
    }
    if set(switch) != allowed_switch_props:
        raise ValueError("unreviewed BCM53125 node properties added")
    if cells(switch["reg"]) != [0] or cells(switch["spi-max-frequency"]) != [781000]:
        raise ValueError("candidate HSSPI chip select or frequency changed")
    if "spi-cpol" not in switch or "spi-cpha" not in switch:
        raise ValueError("candidate must retain the source-backed SPI mode")
    for prop in ("ethernet", "link", "phy-mode", "fixed-link", "phy-handle",
                 "reset-gpios", "dsa,member", "dsa-tag-protocol"):
        if prop in switch:
            raise ValueError("unverified switch contract added: " + prop)

    expected_ports = {1, 2, 3, 4, 8}
    port_path = switch_path + "/ports"
    seen_ports = set()
    for path, props in nodes.items():
        if path.startswith(port_path + "/port@"):
            port = int(path.rsplit("@", 1)[1], 16)
            seen_ports.add(port)
            if set(props) != {"reg"} or cells(props["reg"]) != [port]:
                raise ValueError("unverified switch-port contract added")
            if any(child.startswith(path + "/") for child in nodes):
                raise ValueError("unverified switch-port child node added")
    if seen_ports != expected_ports:
        raise ValueError("candidate port set differs from exact-family evidence")

    for path in ("/soc/ethernet@1000d800", "/soc/switch@10700000",
                 "/soc/mdio@107000b0"):
        if nodes.get(path, {}).get("status") != b"disabled\0":
            raise ValueError("SoC Ethernet/DSA/MDIO node must remain disabled")

    b53_nodes = [path for path, props in nodes.items()
                 if b"brcm,bcm53125" in props.get("compatible", b"").split(b"\0")]
    if b53_nodes != [switch_path]:
        raise ValueError("duplicate or unexpected BCM53125 access path")

    return {"external_switch": "BCM53125-HSSPI-CS0-DISABLED",
            "spi_mode": "MODE3-781KHZ-SOURCE-BACKED",
            "ports": "1-4-AND-8-UNLABELLED",
            "dsa_endpoint": "OMITTED-UNRESOLVED",
            "runtime": "NOT-TESTED"}


def main():
    import libfdt  # Available in the isolated dtschema environment.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dtb", type=Path)
    parser.add_argument("--ethernet-candidate", action="store_true",
                        help="also enforce the disabled Ethernet evidence fixture")
    args = parser.parse_args()
    if not args.dtb.is_file():
        raise ValueError("DTB input must be an existing regular file")
    fdt = libfdt.Fdt(bytearray(args.dtb.read_bytes()))
    nodes = {}
    offset, depth = fdt.next_node(-1, -1)
    while offset >= 0 and depth >= 0:
        props = {}
        prop_offset = fdt.first_property_offset(offset, quiet=(libfdt.NOTFOUND,))
        while prop_offset >= 0:
            prop = fdt.get_property_by_offset(prop_offset)
            props[prop.name] = bytes(prop)
            prop_offset = fdt.next_property_offset(prop_offset, quiet=(libfdt.NOTFOUND,))
        nodes[fdt.get_path(offset)] = props
        offset, depth = fdt.next_node(offset, depth, quiet=(libfdt.NOTFOUND,))
    result = verify(nodes, require_sar=not args.ethernet_candidate)
    if args.ethernet_candidate:
        result["ethernet_candidate"] = verify_ethernet_candidate(nodes)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, ImportError) as exc:
        print("Offline DTB contract failed: " + str(exc), file=sys.stderr)
        raise SystemExit(1)
