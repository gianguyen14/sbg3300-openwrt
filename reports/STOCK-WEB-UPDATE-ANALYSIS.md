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

The previous 2,112-byte divisibility calculations were only an arithmetic observation; they do not prove that the downloaded stock container contains raw physical NAND page+OOB records. Do not classify it as raw NAND without validating the node/writer format.

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

`bcm63xx_flash.c`/`board.c` describe a stock image flash routine; this source mirror is not proof the exact production Web Update endpoint uses it:

- **Observed routine layout** = `[128 KiB tag block][JFFS2 filesystem][optional ROM-D trailer]`. The upload wrapper, exact updater-to-flash path and running build flags remain unverified.
- If the first two bytes are JFFS2 magic `0x1985`, the image is filesystem-only (`ofs=0`); otherwise the first block is treated as the CFE/boot block, the updater injects current NVRAM data at `NVRAM_DATA_OFFSET`, and it skips `ofs=128 KiB` (NAND128) or `16 KiB` (NAND16) when scanning for the `cferam.000` sequence number.
- A 20-byte `WFI_TAG` (crc/version/chipId/flashType/reserved) is read from the image end; version `0x5732`, flash type `3` = NAND128. An all-zero WFI tag fails the `(version & 0xff00) == 0x5700` guard and is tolerated. The stock payload-end WFI area is all zero.
- Filesystem is flashed to MTD `rootfs_update` (fallback `rootfs`) starting at erase block 8 (1 MiB), with `cferam.000` placed in the leading blocks.
- `FILE_TAG` (`bcmTag.h`, MitraStar/Zyxel variant) matches the observed stock tag: MSTC identity, external/internal version, `imageNext` ROM-D flag, and a CRC over the tag checked in `board.c` before flashing.

The source `FILE_TAG` is 256 bytes. CRC is calculated from the beginning of the tag through `TAG_LEN - TOKEN_LEN` (236 bytes); token begins at offset 236 (0xEC). This matches the stock sample's header CRC. The independent stock parser calculates tag CRC `0x4cc2272f`; the tag CRC stored in stock matches it. This confirms header CRC format only, not Web-update acceptability.

- Source web-write path places tagged filesystem at one 128-KiB block before `rootfsAddr`, injects live NVRAM into the first block, then writes via `kerSysBcmImageSet`/MTD; therefore an offline candidate must not embed the current router's NVRAM values.
- Image length accounting in `flashFsKernelImage()` is `rootfsLen + kernelLen + TAG_BLOCK_LEN`; the updater treats rootfs/kernel parts as one JFFS2 system image, seeks optional ROM-D `IMAGE_TAG` at `newImgSize`, validates its CRC, and only writes/erases ROM-D when its image signature requests it. ROM-D appears optional, but exact production build options and stock browser path are not proven.
- The routine `flashWholeImageFile()` is gated by `MSTC_FWUP_FROM_FILE`; this inspected tree alone does not prove that the running SBG3300 build uses that web handler or that it accepts user-submitted whole-image files without further checks.
- Extracted stock boot files (for understanding only): `cferam.000` 182,060 bytes; `vmlinux.lz` 1,624,375 bytes, with a 12-byte header reporting load `0x80020000`, entry `0x8035c520`, compressed data size `0x18c92b`. Not used to create an OpenWrt image.

- The upstream flash path (`kerSysUpdateTagSequenceNumber` / `flashFsKernelImageFile`) rewrites the tag sequence number and toggles the NVRAM bootline `p=` partition flag after writing; dual-image slot selection depends on `curImgSize <= availableSizeTwoImgs` and the partition of the currently booted tag.
- The kernel flash routine itself performs no chip/board/model validation; a ZyXEL "invalid model ID" rejection (as reported in the community thread for SBG3300 web updates) must come from the web application layer, whose source is not present in this tree. Nothing here proves a generated image passes that check.

## Remaining blockers before any candidate

The source informs a plausible internal image structure, but not yet a proven stock-web upload path. Before building anything that could be mistaken for flashable:

1. Confirm whether `MSTC_FWUP_FROM_FILE` is enabled in the exact SBG3300-N000 2018 firmware and find the web handler that calls it.
2. Establish exact `FILE_TAG` identity/model/version values and validation-token CRC byte order/scope from that handler; the observed stock header CRC matches the generic tag CRC range, but that alone does not prove the web request accepts a generated image.
3. Check whether the update UI expects a raw `.bin`, ZIP containing `.bin`/`.rom`/`.bm`, or another envelope, and any ROM-D/version checks.
4. Reconcile the source’s hardcoded JFFS2/CFE sequence-number rewrite and `rootfs_update` MTD selection with the observed board and active-slot layout.
5. Verify non-vendor extraction inputs/licensing and generate only an offline candidate after all format/layout checks pass.

No candidate image has been generated; flashability remains `NOT-FLASHABLE`. Do not upload a trial file.
