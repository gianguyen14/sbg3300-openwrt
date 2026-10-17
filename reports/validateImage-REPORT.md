# cmsImg_validateImage reverse-engineering (MIPS BE)

Evidence: `libcms_util.so` vaddr=file offset in LOAD1; disassembly `/home/hermes/sbg3300-build/validateImage.asm`.

## Signature and behavior

Inferred o32 signature is `int cmsImg_validateImage(void *image, unsigned int imageLen, ... , unsigned char flag)` at 0x14024–0x14034. a0=image bytes; a1=byte length; a2 is an opaque pointer/value passed as ioctl arg; a3 is reduced to its low byte and acts as flag. The function has four ABI args; no separate length beyond a1. Exact semantic type of a2 is not recoverable from this function alone.

Return is local status at 0x144ec: 0 means accepted, 2 means ioctl passed but flag requested the special result, 3 ioctl error, 5 post-check failure; -1 is initialized for checksum mismatch and remains an error status. Null image gives 0 (0x1403c–0x14050), an anomalous permissive path. Return paths depend on helper results described below.

## Ordered pseudocode

```c
status = 0;
if (image == NULL) return 0;                         // 0x1403c-50
if (imageLen >= 0x41) {
  if (cmsImg_isConfigFileLikely(image)) {             // indirect @0x14064-74
    syslog(7, file, 0x405, message);                  // 0x14084- a8
    rc = ioctl(image, imageLen, a2, 0x10000873);       // 0x140b0-d0
    if (rc != 0) { log(..., line 0x409); return 3; }  // 0x140d8-120
  }
}
log(..., line 0x40e);                                // 0x14124-48
if (imageLen >= 0x101 && cmsImg_isConfigFileLikely(image)) { // 0x14150-84
  log(..., line 0x425);                              // 0x14188-a8
  n1 = indirect_helper(); n2 = indirect_helper();     // 0x141b4-d8
  required = n1+n2;                                   // 0x141dc-e4
  if (required < imageLen) { log sizes; goto post; }  // 0x141e8-1440
  status = 1;                                         // 0x14240-48
} else {
  status = -1;
  if (imageLen < 0x15) goto post;                    // 0x14250-64
  p = image + imageLen - 0x14;                       // 0x14268-78
  stored_crc = BE32(p[0..3]);                        // offset imageLen-20..-17, 0x1427c-c0
  calculated = crc_helper(image, imageLen-0x14, -1); // 0x142c4-e8
  if (calculated == stored_crc) {                    // 0x142f0-300
    log(...);
    n = indirect_helper();                           // 0x14334-40
    if (n < imageLen) { log sizes; goto post; }       // 0x14350-3a0
    status = flag ? 2 : 0;                            // 0x143a8-c8
  } else log CRC mismatch (...);                     // 0x143d0-143fc
}
post:
if (status == 1 && another_helper(image)) status=5;   // 0x14440-78
if (status == 2 && another_helper(image)) status=5;   // 0x1447c-b8
log final status; return status;                      // 0x144b8-1500
```

The low-level CRC helper is called with seed `-1` and byte count `imageLen-20`; the four-byte stored word is assembled big-endian at `imageLen-20`. Do not conflate this with the FILE_TAG CRC format supplied externally (little-endian seed 0/no final xor): this routine does not read the FILE_TAG fields at fixed offsets. Exact CRC helper semantics require resolving its indirect target; no explicit final-xor operation appears here. No comparisons against literal model/chip/board/identity/version strings occur in 0x14000–0x14508. These header identity checks, if performed, are delegated to ioctl/helper code and cannot be asserted as this routine's checks.

## Checks vs warnings; calls

The 0x405, 0x40e, 0x425, 0x429, 0x44b, 0x44f, 0x463, 0x465, 0x476 sites are syslog calls (level 7 or 3); they report conditions/sizes and do not themselves reject. Rejection/status effects are the ioctl nonzero path (3), short/CRC mismatch status -1, and post-helper rejection (5). Length thresholds are 0x41 (65), 0x101 (257), minimum CRC-frame size 0x15 (21); helper-derived size sums are compared with imageLen. No 0x120000 flash-limit check appears in validateImage.

Indirect calls from validateImage: likely `cmsImg_isConfigFileLikely` at 0x14064 and 0x14168; syslog at 0x140a4 etc.; ioctl at 0x140d0; two size/config helpers at 0x141bc/d4; CRC helper at 0x142e4; size helper at 0x14340; post validators at 0x14460 and 0x1449c. These are GOT-indirect, and no direct libcms_util function addresses are encoded at call sites. The image is passed to ioctl with request `0x10000873`; this is an ioctl request, not enough evidence to name a specific kernel operation. On the CRC-valid branch, the function performs no image write; image destination is not visible here.

## Related functions

- `cmsImg_getImageFlashSizeLimit` (0x13084): returns 0x00120000 (1,179,648 bytes) directly (`lui v0,0x120`, 0x13090).
- `cmsImg_getImageFlashSize` (0x130a8): ioctl `0xc0184201`, fd 7, output pointer to local word (0x130d8-0xf4); on ioctl error logs and returns 0 (0x13104-40); otherwise returns value.
- `cmsImg_getBroadcomImageTagSize` (0x1315c): returns 0x14 (20 bytes) (0x13168).
- `cmsImg_getConfigFlashSize` (0x13180): helper result multiplied by 4 (0x131a0-c0).
- `cmsImg_willFitInFlash` (0x131e0): ioctl request `0xc0184206`, fd 0, output local word (0x13210-2c); error returns 0; no literal board/model/chip checks visible. (Symbol is at 0x13294 per exports/context; the range here is an additional preceding member, because function extent needs symbol confirmation.)
- `cmsImg_writeValidatedImage` (0x1450c): a0 destination/device-like handle, a1 source image pointer, a2 length, a3 extra value. Calls fopen-like helper on `source+0x1c` with mode 1 (0x14544-5c); failure logs and returns 0x232c (0x14568-bc). On success it builds a 0x1c-byte header, writes length, adds 0x40000000 to header word at +0xc, stores source pointer at header +0x18, then calls helper to write header/data and helper with (a2, header). It closes stream (0x145c4-14680). It does not compare model/chip/board literals. Image source/destination semantic names are not proven by these call sites.

No target strings `'4506'`, `'63268'`, `'963168MXH_17A'`, `'MSTC_3300'` or firmware version comparisons are present in this function's disassembly. Such values belong to stock FILE_TAG metadata and are not acceptance criteria proven by this routine. Likewise, this function does not establish a model/chip/board match.
