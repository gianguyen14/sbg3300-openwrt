# Firmware upgrade CGI reverse-engineering report

## Scope and evidence
Analyzed `/home/hermes/sbg3300-build/stock-rootfs/bin/httpd` offline (MIPS32 big-endian). File offset maps to VA by `0x400000 + offset` for the first LOAD segment. No device access or flash operation performed.

## Routes / handlers
- Strings at file offsets `0xa60a4` (`/firmwareUpgrade-upload.cgi`) and `0xa5f94` (also duplicate log string at `0xa5fbc`: `[httpd] /firmwareUpgrade-uploadpost.cgi (%s)`). Corresponding VAs: `0x4a60a4`, `0x4a5f94`, `0x4a5fbc`.
- `/firmwareUpgrade-fail.cgi` at offset `0xa5fe4` (VA `0x4a5fe4`). `/firmwareUpgrade-upload-restore.cgi` and `/firmwareUpgrade-wwanupload.cgi` follow the upload CGI string at offsets `0xa60c1` and `0xa60e4`.
- The exact pointer words for route string addresses were not found in the file, and a direct lui+addiu address-construction scan found no xref. Route table/function association therefore remains unresolved. `do_upload_post` is a dynamic symbol at VA `0x475e30`, but its disassembly is generic POST-processing/error/reporting logic and does not by itself prove it is the uploadpost route handler. Do not equate it with the firmware-specific handler absent route evidence.
- Dynamic symbol entries identify imported `cmsImg_validateImage` (PLT VA `0x4a3f80`), `cmsImg_writeImage` (`0x4a3f10`), `cmsImg_willFitInFlash` (`0x4a2d70`), `cmsImg_sendLoadStartingMsg` (`0x4a42e0`), `cmsImg_sendLoadDoneMsg` (`0x4a2330`), and `devCtl_setImageState` (`0x4a2390`). Their presence does not establish execution/order in an upload handler.

## Upload behavior: unresolved from located xrefs
Strings include `/tmp/%s` (offset `0xa4a38`, VA `0x4a4a38`) and `/var/tmp/` (offset `0xa499c`, VA `0x4a499c`), but neither was proven to be the firmware upload destination. No upload-parser/handler xref was established; thus multipart parsing, concrete save filename, maximum size, validation/write call ordering and argument values cannot be stated from the evidence gathered. In particular, no evidence was found for `cmsImg_writeValidatedImage` in the dynamic symbols listed.

## Board/model checks and wrapper hints
- `boardID` string is at offset `0xa9c20` (VA `0x4a9c20`) among device-info strings. `chipId` is at `0xb7680` (VA `0x4b7680), followed by `%x` formatting. No occurrences of `4506`, `63268`, or `963168MXH_17A` were found in the binary. No established upload-handler xref demonstrates an httpd-side model comparison or ioctl-based check. Whether `cmsImg_validateImage` enforces compatibility is not established by this httpd-only evidence.
- No hardcoded `.bin`, `.zip`, `.rom`, tag identity or firmware version expectation was established from upload-handler evidence.

## Outcome / flash and state
- Failure redirect string `/firmwareUpgrade-fail.cgi` exists at VA `0x4a5fe4`; no proven conditional branch from an identified firmware handler to it.
- No validated success redirect, user message, image-to-flash behavior, reboot, password/state flag, or direct flash-device/ioctl operation could be associated with this flow from the evidence gathered. Imported CMS image and state functions indicate available APIs only, not proof they are called.

## What was tried / remaining ambiguity
Searched exact route strings and model constants, scanned aligned file words for pointers to the route strings, scanned disassembly for direct lui+addiu constructions, and inspected the `do_upload_post` symbol disassembly. The strings are present, but no direct string xref/route-table entry surfaced. A stronger MIPS control-flow/indirect dispatch analysis is required to identify handler VAs and recover arguments/branches. No unsupported behavior has been inferred.