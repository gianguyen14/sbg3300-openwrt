#!/usr/bin/env python3
"""Audit stock image tag vs public SBG3300 bootlog and BCM family formulas.

Read-only static comparison; no device access. The bootlog is public example
evidence, not the owner's live router session. Do not infer current slot.
"""
import argparse, hashlib, json, re
from pathlib import Path

IMAGE_BASE = 0xBFC00000
FLASH_BASE = 0xB8000000
BOOT_OFFSET = (FLASH_BASE - IMAGE_BASE) & 0xffffffff
TAG_BLOCK = 0x20000
TOTAL_FLASH = 0x08000000
LIVE_ROOTFS = 0x04020000


def ascii_dec(data, off, width, name):
    v=data[off:off+width].split(b"\0",1)[0]
    if not v or not v.isdigit(): raise ValueError(f"invalid tag field {name}")
    return int(v)

def audit(image, bootlog):
    d=Path(image).read_bytes(); txt=Path(bootlog).read_text(errors="replace")
    if d[0:1]!=b"6" or d[4:8]!=b"MSTC": raise ValueError("not stock MSTC tag v6")
    addr=ascii_dec(d,0x5e,12,"rootfsAddress")
    length=ascii_dec(d,0x6a,10,"rootfsLen")
    slot1=(addr+BOOT_OFFSET-FLASH_BASE)&0xffffffff
    slot2_tag=(IMAGE_BASE+TOTAL_FLASH//2+TAG_BLOCK)&0xffffffff
    slot2=(slot2_tag+BOOT_OFFSET-FLASH_BASE)&0xffffffff
    def capture(pattern):
        m=re.search(pattern,txt)
        return m.group(1) if m else None
    boot_image=capture(r"Boot image \(0=latest, 1=previous\)\s*:\s*(\d+)")
    booting_at=capture(r"Booting from latest image \((0x[0-9a-fA-F]+)\)")
    fs_address=capture(r"File system address:\s*(0x[0-9a-fA-F]+)")
    mtd_start=capture(r"(0x[0-9a-fA-F]+)-0x[0-9a-fA-F]+\s*:\s*\"rootfs\"")
    cmdline=capture(r"Kernel command line:\s*([^\n]+)")
    return {
      "stock_sha256":hashlib.sha256(d).hexdigest(),
      "stock_rootfs_address":f"0x{addr:08x}",
      "stock_rootfs_len":f"0x{length:x}",
      "family_formula_slot1_offset":f"0x{slot1:x}",
      "family_inactive_slot2_tag_address":f"0x{slot2_tag:08x}",
      "family_formula_slot2_offset":f"0x{slot2:x}",
      "public_bootlog_boot_image_choice":boot_image,
      "public_bootlog_cfe_latest_image_address":booting_at,
      "public_bootlog_kernel_filesystem_address":fs_address,
  "public_bootlog_rootfs_mtd_start":mtd_start,
  "public_bootlog_cmdline":cmdline,
  "slot2_matches_public_mtd": bool(mtd_start and int(mtd_start,16)==slot2),
  "slot1_matches_public_mtd": bool(mtd_start and int(mtd_start,16)==slot1),
  "meaning":"Public 2016 sample reports slot1-style rootfs offset (0x40000). This is not the owner's 2018 live partition record and cannot establish current active slot.",
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("stock_image",type=Path); p.add_argument("public_bootlog",type=Path)
    a=p.parse_args(); print(json.dumps(audit(a.stock_image,a.public_bootlog),indent=2,sort_keys=True))
if __name__=="__main__": main()
