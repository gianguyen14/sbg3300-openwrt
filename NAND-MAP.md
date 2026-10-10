# NAND map (fail-closed; incomplete)

## Proven controller/chip geometry

The historical stock summary records a Broadcom v4 controller, 128 MiB capacity,
2048-byte writesize, 128 KiB eraseblocks, OOB value 64, ECC-step value 512 and
ECC code 15 with BBT. These records are preserved, but the modern ECC/OOB tuple
is **not confirmed**. Linux brcmnand interprets spare size per 512-byte sector;
legacy code 15 may identify Hamming rather than literal strength 15. The earlier
DTS copied these values into modern properties without resolving that mapping.
The new candidate disables NAND and removes the unverified overrides. Obtain
exact source/geometry evidence before enabling it; no raw device access is used.
The S34ML01G1 part number remains inventory evidence, not a live JEDEC result.
See reports/PRE-FINAL-ENGINEERING.md for the source-level correction.

## Linux partition table observed

| MTD index | Size | Erase size | Label |
|---:|---:|---:|---|
| 0 | `0x016a0000` | `0x20000` | rootfs |
| 1 | `0x00400000` | `0x20000` | data |
| 2 | `0x00020000` | `0x20000` | nvram |

These are logical registered MTD partitions only. Their listing does not
establish the full physical NAND map, CFE location, firmware offsets, reserved
tail, bad-block remapping, or which bytes a stock image writer erases.

## Physical offsets reported by the live kernel

The read-only boot log includes registered physical ranges on `brcmnand.0`:

| Region | Physical start | Physical end (exclusive) | Size | Evidence |
|---|---:|---:|---:|---|
| `nvram` | `0x00000000` | `0x00020000` | `0x00020000` | `dmesg` partition registration |
| unregistered gap | `0x00020000` | `0x04020000` | `0x04000000` | arithmetic only; ownership unknown |
| `rootfs` | `0x04020000` | `0x056c0000` | `0x016a0000` | `dmesg` partition registration |
| unregistered gap | `0x056c0000` | `0x07b00000` | `0x02440000` | arithmetic only; ownership unknown |
| `data` | `0x07b00000` | `0x07f00000` | `0x00400000` | `dmesg` partition registration |
| unregistered tail | `0x07f00000` | `0x08000000` | `0x00100000` | arithmetic only; ownership unknown |

The controller reports total capacity `0x08000000`. This improves the physical
map but does not identify the first gap as CFE, explain firmware logical-address
translation, or describe bad-block-adjusted sector mapping. Preserve every
unregistered region.

## Unknown regions and gate

## Broadcom 4.12L.06B source model (corroborating, not exact-build proof)

The public 4.12L.06B source mirror contains `flash_init_nand_info()` in
`shared/opensource/flash/flash_common.c`. Its 128 KiB-block NAND model computes
the boot block at offset zero, rootfs slot 1 from the next block, rootfs slot 2
from the physical halfway point, a 4 MiB data area before the BBT, and a
1 MiB BBT at the end for devices no larger than 512 MiB. It reserves a block
for ROM-D/metadata immediately before data in this build configuration. These
constants explain the live data start at `0x07b00000` and tail at
`0x07f00000` (128 MiB total), and are strong corroboration of those regions.

The source also explicitly accounts for bad blocks when choosing rootfs
addresses and tracks rootfs bad-block counts for image-tag lookup. This means a
simple contiguous logical-image-to-physical-offset assumption is not justified.
The matching-family header defines a 128 KiB boot-ROM reservation and places
the NVRAM structure at offset `0x580` within the first eraseblock. This is
consistent with the live `nvram` MTD entry aliasing the first block rather than
being an independent physical partition. Its computed second rootfs slot
starts at the 64 MiB midpoint; adding one 128 KiB tag/kernel block yields
`0x04020000`, exactly the start of the live `rootfs` MTD registration. This is
strong cross-evidence for the slot-2 interpretation. The live MTD only exposes
the active image extent (`0x04020000..0x056c0000`); it does not report the full
reserved slot size. The 2015 source mirror is not proven identical to the 2018
running build, so this still does not close image-writer or bad-block safety.

Relevant source locations, recorded for local reproduction:

- `source/vendor/bcm963xx_4.12L.06B_consumer/shared/opensource/flash/flash_common.c`:
  `flash_init_nand_info()` layout calculations and BBT/data constants.
- `source/vendor/bcm963xx_4.12L.06B_consumer/bcmdrivers/opensource/char/board/bcm963xx/impl1/bcm63xx_flash.c`:
  NAND image selection, bad-block handling, and image-tag address calculations.
- `source/vendor/bcm963xx_4.12L.06B_consumer/shared/opensource/include/bcm963xx/bcm_hwdefs.h`:
  NAND partition indices and data/BBT size constants.

Do not translate the inferred two-slot scheme into OpenWrt fixed partitions
until matching Zyxel 2018 source or binary behavior resolves the live rootfs
extent, active-slot selection, CFE placement and bad-block translation.

| Region/behavior | Status |
|---|---|
| CFE physical start/size and bad-block semantics | PARTIAL; matching-family source models first 128 KiB as boot and has bad-block-aware image addressing, but running build equivalence is unproven |
| Kernel/rootfs physical range and writer layout | PARTIAL; matching-family source describes two slots, while exact active rootfs extent and kernel/tag placement remain unexplained |
| Data partition physical start/end | PROVEN from boot log as `0x07b00000..0x07f00000` |
| NVRAM physical location and write semantics | PARTIAL; registered range `0..0x20000`, contents/erase behavior unknown |
| Reserved tail/BBT/CET placement | STRONGLY-INFERRED; source model places a 1 MiB BBT at `0x07f00000..0x08000000`, exact runtime implementation unproven |
| OpenWrt UBI/UBIFS compatibility | UNKNOWN |

No writable image, sysupgrade layout, or stock-web wrapper is permitted until
all boot-critical ranges and bad-block/ECC behaviors are proven from exact
source/binary behavior. No raw NAND operations are part of this project.
