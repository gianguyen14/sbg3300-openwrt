# SBG3300-N000 web-update acceptance recipe (REVERSE-ENGINEERED, stock-verified)

Status: OFFLINE RESEARCH ONLY. No image was created or uploaded. Flashing any
self-made image remains forbidden and unverified (kernel/CFE boot untested).

Source of truth: stock `V1.01(AADY.9)C0.bin` (SHA256
3b994309aec554c858d8129c17ff1966b11ec33cb9f3e77914bcf211f0310b79) + MIPS BE
binaries extracted from its JFFS2 rootfs (`httpd`,
`lib/public/libcms_util.so`), cross-verified with the stock file bytes and CRCs.

## Verified upload chain (vaddr evidence in upgrade-chain-REPORT.md)

1. Browser posts multipart/form-data, field `filename`, extension must be `.bin`
   (client check) to `/pages/tabFW/firmwareUpgrade-upload.cgi`.
2. `do_upload_pre_MSTC` (httpd 0x4777b4) -> `upLoadImage` (0x476ef4) keeps the
   upload in RAM (`imgBuf` 0x4eab34 / `imgLen` 0x4eab38); no temp file for the
   firmware path (type 3 = WWAN package goes to /var/fw/ras.bin).
3. `cmsImg_willFitInFlash` (libcms_util 0x13294): imageLen+0x100 < flash size.
4. `cmsImg_validateImage` (0x14000, flag=0):
   - config-file path (starts `<?xml version` + `<DslCpeConfig` @+0x14):
     `sendConfigMsg(...,0x10000873)`; "config verified" -> status 3 (rejected
     for firmware).
   - else `verifyBroadcomFileTag` (imageLen >= 0x101): status 1 = PASS.
   - else trailing CRC path: status 0 = REJECT by httpd (0x267b illegal image).
   - status 5 = model mismatch (0x2680 illegal model id).
5. `do_upload_post` (0x475e30): `devCtl_setImageState(0x30)` ->
   `cmsImg_writeImage` (0x13550, re-validates) -> `cmsImg_writeValidatedImage`
   -> `devCtl_boardIoctl` CMS cmd `0x10000876` (kernel flash) ->
   `cmsUtil_sendRequestRebootMsg` (reboot).
   glbUploadStatus: 0=OK, 0x267b illegal image, 0x2680 illegal model id,
   0x2681 illegal boot rom size, 0x2682 WWAN, 0x232c OOM.

## What the web validator requires of the file (ALL verified against stock)

Byte offsets relative to file start (FILE_TAG, ASCII fields):

| off  | field        | stock value        | check in validator (verifyBroadcomFileTag) |
|------|--------------|--------------------|--------------------------------------------|
| 0x00 | tagVer       | "6"                | eq '6'                                     |
| 0x04 | identity     | "MSTC_3300"        | eq "MSTC" @+4                              |
| 0x09 | family (MRD) | "3300"             | vs NVRAM hex model id                      |
| 0x0e | model (TAG)  | "4506"             | eq NVRAM model id or "4506" (verifyModelId_MSTC 0x11cd8) |
| 0x26 | chipId       | "63268" (hex)      | strtol(...,16) == devCtl_getChipId() (0x63268) |
| 0x2c | boardId      | "963168MXH_17A"    | not checked in userspace (stock carries it) |
| 0x3e | imageLen(sz) | "23724032"         | payload size = 0x20000 + parser length, <= flash+20 |
| 0xd8 | image CRC    | BE32 0xfa13f3d1    | crc32_raw(seed 0xFFFFFFFF, NO final xor) over [0x20000, 0x20000+len) |
| 0xec | header CRC   | BE32 0x4cc2272f    | crc32_raw(seed 0xFFFFFFFF, NO final xor) over [0x00000, 0x00ec) |

- File size >= 0x800 (2048) and <= flashSize + 20.
- NO JFFS2 magic / 0x1985 check anywhere in httpd or libcms_util.so (byte
  pattern absent from both binaries).
- The "illegal model id" error originates in `verifyModelId_MSTC` comparing the
  image TAG model ("4506") / family ("3300") against the unit NVRAM model id.
  `check_modelid` (0x15048) is NOT part of upload: it runs at boot from
  web_main and migrates NVRAM model `4506` -> `3300` (BCD 0x33 0x00), i.e. the
  unit NVRAM keeps 3300-family identity.
- CRC convention (both tag CRCs): the BCM `getCrc32` variant,
  crc32(0xFFFFFFFF, data) without final XOR == zlib.crc32(data) ^ 0xFFFFFFFF.
  (NOTE: different from the JFFS2-on-disk CRC crc32_le(seed=0, no final xor).)

## What is still kernel/CFE-side (NOT verified by web layer)

- The payload after 0x20000 must be a valid bootable image for BCM CFE+kernel:
  JFFS2 with `cferam.000` and `vmlinux.lz` dirents (per board.c
  flashFsKernelImageFile / kernel rootfs mounting), tag sequence number and
  dual-image partition rules, NVRAM rewrite of bootline p= flag.
- A generated OpenWrt image has NEVER been booted on SBG3300-N000; initramfs
  CFE/RAM boot is unverified. Nothing here proves a generated image boots or
  that flashing is safe.

## Verification gates before considering a wrapped OpenWrt payload

Current OpenWrt output is not ready to wrap. See `OPENWRT-WEBUPDATE-PAYLOAD-AUDIT.md` for independently checked structures, sizes, hashes, build rules, and the missing CFE/JFFS2 layout. The sysupgrade is a tar (kernel + SquashFS root), the initramfs is an ELF, and the intermediate CFE kernel JFFS2 has only `vmlinux.lz` plus OpenWrt marker dirents, no `cferam.000`. Therefore do not tag/wrap it as a candidate: a valid MSTC wrapper would pass the web gate and permit an unsafe write, not serve as a harmless parser test.

1. Generate a complete JFFS2 payload using the stock update-path layout, including verified boot files and the correct kernel/root arrangement; do not rely on matching lengths alone.
2. Establish source evidence for all CFE/kernel expectations, image sequence/slot handling, NVRAM injection and live MTD boundaries for this precise SBG3300 build.
3. Validate only offline and maintain a deliberately invalid/non-flashable status until an authorized hardware boot path and hardware evidence exist.

No wrapper, image candidate, upload, flash, or sysupgrade has been created/performed. `NOT-FLASHABLE` remains active.