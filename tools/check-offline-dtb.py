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


def verify(nodes):
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
    if sar is None or sar.get("status") != b"disabled\0":
        raise ValueError("SAR contract fixture missing or active")
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
    return {"sar": "DISABLED", "topology": "UNRESOLVED-DISABLED",
            "nand": "DISABLED-UNRESOLVED-ECC-OOB", "console": "UNSELECTED",
            "runtime": "NOT-TESTED", "image_safety": "NOT-FLASHABLE"}


def main():
    import libfdt  # Available in the isolated dtschema environment.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dtb", type=Path)
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
    print(json.dumps(verify(nodes), indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, ImportError) as exc:
        print("Offline DTB contract failed: " + str(exc), file=sys.stderr)
        raise SystemExit(1)
