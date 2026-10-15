# SBG3300-N000 stock firmware and image-format research

Date: 2026-10-13

## Scope and safety

Read-only analysis of the stock firmware stored in the public project repository. No router upload, flash, reboot, reset, UART, raw MTD read, or NAND write was performed. This report does not approve any image for installation.

## Source artifact

- Repository: `gianguyen14/sbg3300-openwrt`, branch `main`
- Path: `V1.01(AADY.9)C0.bin`
- Fetched from `https://raw.githubusercontent.com/gianguyen14/sbg3300-openwrt/main/V1.01(AADY.9)C0.bin` using HTTP byte ranges and verified `Content-Range` per chunk.
- Size: 23,876,705 bytes
- SHA256: `3b994309aec554c858d8129c17ff1966b11ec33cb9f3e77914bcf211f0310b79`
- Local evidence copy: `/home/hermes/sbg3300-build/reference-stock-aady9.bin`

## Tag findings

The Broadcom-style tag occupies the first `0x20000` bytes; payload begins at file offset `0x20000`. Observed fields include:

- Tag version: `6`
- Identity/signature: `MSTC_3300` (followed by a separate `4506` field)
- Product/model code: `4506`
- Chip ID: `63268`
- Board ID: `963168MXH_17A`
- Firmware version: `V1.01(AADY.9)`
- Declared tagged payload length: `23,724,032` (`0x16c0000`) bytes
- CFE address/length fields: zero
- Kernel address/length fields: zero
- Trailer flag: `1`
- Trailer starts at `0x16c0000`, is 21,601 bytes, and has a textual LZW marker followed by opaque bytes. The trailer format and semantics are unknown.

The physical NAND has 128 MiB capacity, 2 KiB page, 64-byte OOB, and 128 KiB eraseblocks per prior live readout. How this stock file is encoded/written to NAND—including ECC/OOB and bad-block mapping—remains unknown.

## Stock payload encoding observations (inconclusive)

- Stock image: 23,876,705 bytes = 11,305 full 2,112-byte page+OOB records plus 545 bytes.
- Stock tag declares payload length 23,724,032 = 11,233 full page+OOB records plus 1,664 bytes; it is divisible by 128 KiB eraseblocks.
- The 545-byte file remainder consists of a 256-byte trailer header plus 289 bytes, so the file length is consistent with an appended trailer around an eraseblock-aligned tagged payload; it does not establish whether all payload records are physically raw NAND pages or whether a downloader strips/rewrites portions.
- The stock image payload starts with `19 85 e0 ...` record-like bytes, not a normal kernel magic; this resembles page/OOB encoding but is not decoded or proven.
- JFFS2 signatures confirm the payload contains a JFFS2 filesystem with CFE boot artifacts: `cferam.000`, kernel blob (`vmlinux.lz`-like), `busybox`, shared libraries, web UI assets, and a `CFE1CFE1` boot chain near the start of the filesystem region. Name offsets are approximate (±1-2 bytes) because this Broadcom/CFE JFFS2 variant does not follow the stock Linux `jffs2_raw_dirent` layout exactly; the filesystem was not fully decoded. The `cferam.000` + kernel + rootfs JFFS2 structure is what CFE expects, so rebuilding a flashable container would require, at least: an exact decoder for this JFFS2 variant, correct NAND ECC/OOB/bad-block writer mapping, and the updater's validation rules (including any signature/version policy) — none of which are established.

## Offline integrity checks

`tools/sbg3300-image-info` was corrected to parse the stock MSTC identity and checksum roles accurately. Its offline checks against the stock file report:

- Header CRC computed/stored: `0x4cc2272f` / `0x4cc2272f` — match.
- Tagged payload range: `[0x20000, 0x16c0000)`.
- Payload CRC: `0xfa13f3d1`; it matches both the image CRC field at `0xd8` and rootfs CRC field at `0xdc` in this stock file.
- Trailer CRC computed/stored: `0xbd3e9d8c` / `0xbd3e9d8c` — match.
- Project regression suite: 32 tests pass, including parser bounds/CRC and offline DTS contracts.

These checks confirm internal consistency of the stock sample, not Zyxel Web Update acceptance rules or flash layout safety.

## Generated candidate audit

The old candidate `/home/hermes/sbg3300-build/output-firmware/openwrt-sbg3300-n000-web-flashable-cfe.bin` is **not a valid stock-compatible Web Update image**:

- It uses `Broadcom Corporatio` where stock uses `MSTC_3300`.
- Its declared tagged payload exceeds its file length; the corrected offline parser rejects it.
- Its tag semantics and trailer do not match the stock container.

Do not upload it. The `openwrt-...-squashfs-sysupgrade.bin` is a TAR intended for sysupgrade from a running OpenWrt instance, not stock Zyxel firmware update.

## Stock updater format (from BCM 4.12L.06B source)

`bcm63xx_flash.c`/`board.c` implement the web-update flash path:

- **Container accepted by the updater** = `[128 KiB tag block][JFFS2 filesystem][optional ROM-D trailer]`. The web upload is consumed as logical bytes; ECC/OOB is added by the NAND controller on MTD writes. The earlier raw page/OOB "candidate" label was a hypothesis and is superseded by source-level reading.
- If the first two bytes are JFFS2 magic `0x1985`, the image is filesystem-only (`ofs=0`); otherwise the first block is treated as the CFE/boot block, the updater injects current NVRAM data at `NVRAM_DATA_OFFSET`, and it skips `ofs=128 KiB` (NAND128) or `16 KiB` (NAND16) when scanning for the `cferam.000` sequence number.
- A 20-byte `WFI_TAG` (crc/version/chipId/flashType/reserved) is read from the image end; version `0x5732`, flash type `3` = NAND128. An all-zero WFI tag fails the `(version & 0xff00) == 0x5700` guard and is tolerated. The stock payload-end WFI area is all zero.
- Filesystem is flashed to MTD `rootfs_update` (fallback `rootfs`) starting at erase block 8 (1 MiB), with `cferam.000` placed in the leading blocks.
- `FILE_TAG` (`bcmTag.h`, MitraStar/Zyxel variant) matches the observed stock tag: MSTC identity, external/internal version, `imageNext` ROM-D flag, and a CRC over the tag checked in `board.c` before flashing.

## Consequences and remaining blockers to Web Update

A web-update-shaped image is constructible offline: 128 KiB MSTC tag block (valid tag CRC) + JFFS2 containing `cferam.000` (182,060 B, extracted from stock) + kernel + rootfs. OpenWrt already ships matching pieces: `imagetag` (custom signature/board id), `mkfs.jffs2`, and the `cfe-wfi-tag` recipe. Still unproven before generating one:

1. Exact `FILE_TAG` `tagValidationToken` CRC scope in the updater's pre-flash check (board.c ~line 2187).
2. Whether the ROM-D trailer (`IMAGE_TAG` + LZW blob) is mandatory or optional.
3. Runtime NAND writer/bad-block behavior: cferam sequence rewrite and `rootfs_update` MTD availability inside the stock kernel.

No candidate image was generated. Flash readiness remains `NOT-FLASHABLE`; no upload should be attempted.
