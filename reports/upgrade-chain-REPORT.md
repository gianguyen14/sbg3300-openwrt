# ZyXEL SBG3300-N000 web firmware-upgrade validation chain — full RE report

Offline static RE of `stock-rootfs/bin/httpd` (MIPS32 BE, non-PIC EXEC,
LOAD1 vaddr=0x400000+fileoff for bytes 0..0xd24e4, LOAD2 vaddr 0x4e3000=fileoff 0xd3000,
gp=0x4f04e0) and `stock-rootfs/lib/public/libcms_util.so` (DYN, first LOAD vaddr==fileoff 0..0x26a34,
LOAD2 vaddr 0x37000=fileoff 0x27000, **gp = 0x40630** = PLTGOT 0x38640 + 0x7ff0).
All GOT slot values quoted below are the in-file link-time contents; for the EXEC they equal runtime
addresses, for the .so the loader adds the same bias to every slot, so targets are identified exactly.
The context file's "gp=0x3eff0 for libcms_util.so / slot vaddr = gp+off" was wrong; correct gp is
0x40630 (prologue `lui $gp,3; addiu $gp,$gp,-0x39d0; addu $gp,$gp,$t9` at 0x14000 → gp=0x2c630+0x14000=0x40630).
Imported symbols are resolved through the dynsym stub table (UNDEF size-0 symbols carry stub vaddrs, e.g.
0x22480=sysGetNVRAMFromFlash, 0x223e0=sysSetNVRAMToFlash, 0x220c0=memcpy, 0x222f0=cmsMsg_sendAndGetReply,
0x22440=cmsMsg_getHandleEid, 0x221d0=devCtl_boardIoctl, 0x22270=devCtl_getChipId, 0x22230=strtol,
0x1a0d0=cmsCrc_getCrc32, 0x5ef0=log_log, 0x7614=cmsMem_alloc, 0x7a80=cmsMem_free).

Key correction vs previous findings: **check_modelid is NOT called from upLoadImage / upLoadImageFile /
do_upload_pre_MSTC.** It is called once from `web_main` while servicing an SMD message (httpd 0x414ac0),
i.e. a boot-time NVRAM board-ID migration. The model check inside the upload path is
`verifyModelId_MSTC` / `verifyModelId_BRCM` (called from inside cmsImg_validateImage). Also, the
ioctl-ish call with 4th arg 0x10000873 is not a failure path: it is `sendConfigMsg(image,len,msgElm,0x10000873)`
and **return 0 means "CMS XML config verified"** → validateImage returns 3; the "config file" classification
is what httpd then rejects (or accepts on the restore page).

Disassembly dumps of all six target functions (plus all helpers cited below) are in
`/home/hermes/sbg3300-build/upgrade-chain-asm/`.

---

## 1. cmsImg_validateImage — libcms_util.so 0x14000–0x146a8

Signature (confirmed by httpd call site 0x477948-0x477950 and internal call 0x1358c):
`u32 cmsImg_validateImage(u8 *image, u32 imageLen, u32 msgHandle/a2, u32 flag/a3)`
Local var at fp+0x38 = `status` (init 0).

Precise pseudocode:

```
status = 0
if image == NULL: return 0                                  # 0x1403c-0x1404c
if imageLen >= 0x41 (65):                                    # 0x14054-0x14060  sltiu 0x41
    if cmsImg_isConfigFileLikely(image):                     # 0x14068 GOT[-0x7eb8]->0x133ec ; call 0x14070
        log(7,"cmsImg_validateImage",0x405,"possible CMS XML config file format detected")  # 0x14084-0x140a8
        ret = sendConfigMsg(image, imageLen, a2, 0x10000873) # 0x140b0-0x140d0, target 0x1450c
        #  a0=image, a1=imageLen, a2=msgElm(a2 passthrough), a3=0x10000873 (lui 0x1000|ori 0x873 @0x140bc-0x140c0)
        if ret == 0:                                         # bnez -> 0x14124 (0x140e4)
            log(7,"cmsImg_validateImage",0x409,"CMS XML config format verified.")
            return 3                                         # 0x14118
# --- not a (verified) config file ---
log(7,"cmsImg_validateImage",0x40e,"not a config file")      # 0x14124-0x14148
if imageLen < 0x101 (257): goto CRC_ONLY                    # 0x14150-0x14158
if verifyBroadcomFileTag(image) != 0: goto CRC_ONLY          # 0x14160-0x14174 target 0x12488 ; bnez->0x14250
# ----- Broadcom-tag (“flash”) format, status 1 -----
log(7,"cmsImg_validateImage",0x425,"Broadcom format verified.")      # 0x14188
maxSize = cmsImg_getImageFlashSize() + cmsImg_getBroadcomImageTagSize()  # 0x141b4(->0x130a8) + 0x141cc(->0x1315c ; returns 0x14=20)
if maxSize < imageLen:                                        # 0x141e8-0x141f4 sltu
    log(3,"cmsImg_validateImage",0x429,"broadcom image is too large for flash, got %u, max %u")
    goto DONE                                                 # status stays 0
status = 1                                                    # 0x14240
goto DONE
# ----- CRC_ONLY (“whole flash image” fallback) -----
CRC_ONLY: (0x14250)
crc = 0xFFFFFFFF                                              # 0x14250-0x14254 addiu -1
if imageLen < 0x15 (21): goto DONE                            # 0x14258 sltiu 0x15
p   = image + imageLen - 0x14 (20)                            # 0x14268-0x14278
stored = BE32(p[0..3])                                        # 0x14280-0x142bc (lbu shifts -> big-endian word)
crc = cmsCrc_getCrc32(image, imageLen-0x14, 0xFFFFFFFF)       # 0x142d8-0x142e4 (->0x1a0d0), a2 seed = -1
if crc != stored:                                             # 0x142f4 bne -> 0x143d0
    log(3,"cmsImg_validateImage",0x463,"Could not determine image format [%d bytes]")   # 0x143d0-0x143f8
    log(7,"cmsImg_validateImage",0x465,"calculated crc=0x%x image crc=0x%x")             # 0x14404-0x14434
    goto DONE                                                 # status unchanged (0)
log(7,"cmsImg_validateImage",0x44b,"Whole flash image format [%ld bytes] verified.")     # 0x14304-0x1432c
if cmsImg_getImageFlashSize() < imageLen:                     # 0x14338-0x14358
    log(3,"cmsImg_validateImage",0x44f,"whole image is too large for flash, got %u, max %u")
    goto DONE
status = (flag != 0) ? 2 : 0                                  # 0x143a8-0x143c4 (lbu 0x5c(fp))
# ----- DONE: model verification for the two recognized firmware classes -----
DONE: (0x14440)
if status == 1:                                               # 0x14444-0x14448
    if verifyModelId_MSTC(image) != 0: status = 5             # 0x14450-0x14478 (->0x11cd8 ; 5 = model mismatch)
if status == 2:                                               # 0x1447c-0x14484
    if verifyModelId_BRCM(image) != 0: status = 5             # 0x1448c-0x144b4 (->0x12168)
log(7,"cmsImg_validateImage",0x476,"returning image format %d", status)   # 0x144b8-0x144e0
return status
```

**Return contract (what callers must do with it):** status ∈ {0,1,2,3,5}.
- 3 = verified CMS XML config file (sendConfigMsg to 0x10000873 answered 0). Not a firmware image.
- 1 = verified Broadcom-tag firmware (“Broadcom format verified.”), size fits flash+20, MSTC model verified.
- 2 = CRC-verified whole-flash image AND caller set flag(a3)!=0, size ≤ flash, BRCM model verified.
- 5 = model-ID mismatch (verifyModelId_MSTC/BRCM returned 0x2680).
- 0 = everything else (image==NULL, whole-flash with flag==0, size overruns, CRC mismatch → unknown format).
**The CRC mismatch branch does NOT set an error status itself — it logs and leaves status 0.**
But both httpd (0x4779a4: ret==0 → “invalid image format”, glbUploadStatus=0x267b) and
cmsImg_writeImage (0x135b0: ret==0 → return 0x267b) treat 0 as REJECT, so the trailing 20-byte CRC
**is in effect mandatory** for the whole-flash classification, and the whole-flash class itself is
rejected by the web path (httpd always calls with a3=0 → status 0 → 0x267b). Only status 1
(Broadcom-tag) passes the web upgrade; status 5 → "invalid image model id" (0x2680).

### sendConfigMsg — embedded 0x1450c–0x14700 (the call with 4th arg 0x10000873)
```
sendConfigMsg(image, imageLen, msgElm, cmd)
  buf = cmsMem_alloc(imageLen + 0x1c, 1)                      # 0x1454c-0x1455c (a0=len+0x1c)
  if !buf: log(3,"sendConfigMsg",0x485,"failed to allocate %d bytes for msg 0x%x"); return 0x232c (9004, CMS_E_NOMEM)
  p=buf: p[0]  = cmd            (0x10000873)                  # 0x145dc
         p[4]  = cmsMsg_getHandleEid(msgElm)                  # 0x145e4-0x14604
         p[8]  = 0x14 (20)                                    # 0x1460c
         p[0xc]|= 0x40000000                                  # 0x14618-0x14624 flag bit
         p[0x18]= imageLen                                    # 0x1462c
         memcpy(p+0x1c, image, imageLen)                      # 0x14634-0x14648 (->0x220c0 memcpy)
  ret = cmsMsg_sendAndGetReply(msgElm, p)                     # 0x14654-0x14664 (->0x222f0)
  cmsMem_free(buf)                                            # 0x14674-0x14680
  return ret        # 0 == verified/consumed
```
0x10000873 = CMS board/daemon command ID (0x10000000 | 0x873); 0x10000875/0x10000876 are used by
cmsImg_writeValidatedImage for config/other writes (0x13890, 0x13808).

### Helper evidence
- cmsImg_isConfigFileLikely 0x133ec: memcmp(image, "<?xml version"@0x25114, strlen) == 0 AND
  memcmp(image+off, "<DslCpeConfig"@0x25124, strlen)==0 for some off in [0x14..0x31] (loop 0x1349c-0x134f0) → 1 else 0.
- verifyBroadcomFileTag 0x12488 (“verifyBroadcomFileTag” string @0x257d0):
  ```
  log(7,"verifyBroadcomFileTag",0xfc,"start of pTag=%p tagversion %02x %02x %02x %02x", image, image[0..3])
  tokenCrc = BE32(image+0xec)                                 # 0x12520
  imageLen = BE32(image+0xd8)                                 # 0x12530 (base for payload crc; also atoi(image+0x3e) logged as "totalImageLen=%d" @0x12640)
  if cmsCrc_getCrc32(image, 0xec, -1) != tokenCrc:            # 0x12544-0x12574
      log(7,..,"token crc failed, this is not a valid broadcom image"); log(..,"calculated crc=0x%x tokenCrc=0x%x"); return 0x267b
  log(7,..,"header CRC is OK.")                               # 0x125f0
  totalImageLen = atoi(image+0x3e)                            # 0x1261c-0x1263c (ASCII decimal field)
  if cmsCrc_getCrc32(image+0x20000, totalImageLen, -1) != BE32(image+0xd8):   # 0x12674-0x126b8
      log(3,.."image crc failed after broadcom header crc succeeded"); log(.."calculated crc=0x%x imageCrc=0x%x totalImageSize=%d"); return 0x267b
  log(7,..,"image crc is OK")                                 # 0x1273c
  if atoi(image) != atoi("6"@0x24ed8) (=6):                   # 0x12768-0x127b0 (image byte 0 must be ASCII '6')
      log(3,..,"Firmware tag version [%d] is not compatible with the current Tag version [%d]"); return 0x267b
  log(7,..,"tarVer=%d, curVar=%d")                            # 0x12800
  if matchChipId(image+0x26, image+0x18) == 0:                # 0x1283c-0x1286c (->0x11bf0)
      log(3,..,"chipid check failed"); return 0x267b
  log(7,..,"Good broadcom image"); return 0
  ```
- matchChipId 0x11bf0: `strtol(image+0x26, NULL, 16) == devCtl_getChipId()` (0x11c1c-0x11c64;
  strtol->0x22230, devCtl_getChipId->0x22270); equal → 1 else log(3,"matchChipId",0x66,
  "Chip Id error.  Image Chip Id = %04x, Board Chip Id = %04x."@0x24bc0) → 0.
- cmsCrc_getCrc32 0x1a0d0: table-driven CRC-32, table @0x38210 (table[1]=0x77073096 → IEEE 802.3 / zlib
  polynomial 0xEDB88320), `crc = (crc>>8) ^ table[(crc ^ *p++) & 0xff]` for len bytes, **no final XOR**;
  seed = a2 (all callers pass 0xFFFFFFFF). So the whole-flash check is:
  `BE32(image[imageLen-20 .. imageLen-17]) == crc32_raw(image[0..imageLen-20], seed=0xFFFFFFFF)`.
- cmsImg_getImageFlashSize 0x130a8: CMS call with cmd a0=0xc0184201, a1=7, a2=0, a3=0, out=&size
  (callee GOT[-0x7d38]->0x221d0 = devCtl_boardIoctl); failure → 0 + log "Could not get flash size"@0x25098.
- cmsImg_getBroadcomImageTagSize 0x1315c: returns literal 0x14 (20).
- verifyModelId_MSTC 0x11cd8 / verifyModelId_BRCM 0x12168 → see §2b below.

## 2. check_modelid — libcms_util.so 0x15048–0x153b0  (void)

```
check_modelid():                                            # no args; no meaningful return value
  u8  nvram[0x400]     @ fp+0x2c
  char s[8]            @ fp+0x42c
  if sysGetNVRAMFromFlash(nvram) == 0:                      # 0x15074-0x15080 (->0x22480)
      sprintf(s, "%02x%02x"@0x24bfc, nvram[0x2dc], nvram[0x2dd])   # 0x15094-0x150cc  (lb @0x150a4,0x150b4)
  if strcmp(s, "4506"@0x24cb8) != 0:                        # 0x150d8-0x150fc (->0x22590)
      return                                                # MISMATCH: silent early return (0x150fc bnez -> 0x15394)
  # ---- MATCH ("4506") ----
  log(3,"check_modelid"@0x25694, 0x56d, "model ID from %s change to %d"@0x25674, s, g_model)   # 0x15104-0x15140
  g_model = *(u32*)0x380c0        # in-file value 0x00000ce4 = 3300  (SBG3300)   # 0x1510c-0x15110
  v100 = g_model / 100            # 33  (magic 0x51eb851f >>5)                  # 0x15154-0x151b4
  vrem = g_model % 100            # 0                                     # 0x151b8-0x15210
  nvram[0x2dc] = BCD(v100)        # (v100/10)<<4 | v100%10 = 0x33         # 0x15270-0x1528c -> fp+0x308 = fp+0x2c+0x2dc
  nvram[0x2dd] = BCD(vrem)        # 0x00                                # 0x15280-0x1528c -> fp+0x309 = fp+0x2c+0x2dd
  sprintf(s, "%02x%02x", nvram[0x2dc], nvram[0x2dd])        # 0x15290-0x152c8  (= "3300")
  crc = cmsCrc_getCrc32(nvram, 0x400, 0xFFFFFFFF)           # 0x152d4-0x15304 (->0x1a0d0)
  *(u32*)(fp+0x428) = crc                                    # stored at end of the 0x400-byte image? no: fp+0x428 == nvram+0x3fc .. see note
  if sysSetNVRAMToFlash(nvram) == 0:                        # 0x15310-0x15320 (->0x223e0)
      log(7,"check_modelid",0x580,"Change nvramData FeatureBits"@0x24d64)        # 0x15334-0x15354
  else:
      log(3,"check_modelid",0x583,"Change nvramData FeatureBits Error"@0x24d84)  # 0x15368-0x15388
  return
```
(fp+0x428 == buf + (0x428-0x2c) = buf[0x3fc..0x3ff], i.e. the NVRAM image's own trailing 4-byte CRC
field inside the 0x400B image — so the image IS re-CRC'd in place and sysSetNVRAMToFlash persists it.
The two modified model bytes are 0x2dc/0x2dd. The sprintf at fp+0x42c writes 5 bytes one past the buffer
(buf+0x400), a harmless off-by-one.)

**The struct at fp+0x2c** = the raw NVRAM flash image (0x400 bytes) as produced/consumed by
sysGetNVRAMFromFlash / sysSetNVRAMToFlash (imports resolved to libcms_core/libcms_boardctl at runtime;
"sysGetNVRAMFromFlash" string present in libcms_core.so @0xa8ee, libcms_boardctl.so @0x843, etc.).
**The two bytes** nvram[0x2dc], nvram[0x2dd] = the board/model field (two hex digits each, rendered as
"%02x%02x"): together they encode the 4-hex-digit board type, e.g. 0x45 0x06 = "4506". The adjacent
field nvram[0x2da..0x2db] must hold "MS" (checked by verifyModelId_MSTC), so this is ZyXEL's
"MS [model source]" + board-ID header inside the NVRAM image.

**Match vs mismatch return:** the function is void and never returns a status. MATCH ⇒ NVRAM bytes
0x2dc/0x2dd rewritten from {0x45,0x06} ("4506") to BCD{3300} = {0x33,0x00} ("3300"), flash updated,
two log lines. MISMATCH ⇒ immediate silent return, NVRAM untouched.

### 2b. verifyModelId_MSTC 0x11cd8 / verifyModelId_BRCM 0x12168 (the real model checks)
```
verifyModelId_MSTC(image):                       # called by validateImage for status==1 (Broadcom-tag image)
  sysGetNVRAMFromFlash(nvram@fp+0x20)
  if read fails: log(3,..,"Get MRD information fails, just fall through"@0x24d34); return 0x2680
  strncpy(prefix, nvram+0x2da, 2)                 # fp+0x420
  sprintf(mrd, "%02x%02x", nvram[0x2dc], nvram[0x2dd])   # fp+0x424
  strncpy(t_ident, image+4, 4)                    # fp+0x42c   — image[4..7]
  strncpy(t_mrd,   image+9, 4)                    # fp+0x434   — image[9..12]
  memcpy(t_tag,    image+0xe, 4)                  # fp+0x43c   — image[14..17]
  if strcmp(prefix, "MS"@0x24c7c) != 0: log(3,..,"Not find MSTC identify, just fall through"@0x24d08); return 0x2680
  if strcmp(t_ident, "MSTC"@0x24c80) != 0:        # image[4..7] must literally be "MSTC"
      log(3,..,"Not find MSTC identify, just fall through"); return 0x2680
  log(7,..,"Finds ZyXEL identity, start checking model ID"@0x24c88)
  if strcmp(mrd, t_mrd)==0  or  strcmp(mrd, t_tag)==0  or  strcmp(t_mrd, "4506"@0x24cb8)==0:
      log(7,..,"Check modelID successfully"@0x24cec); return 0     # 0x120b0-0x120dc
  log(3,..,"Check model from TAG is different with MRD"@0x24cc0)
  return 0x2680                                          # 0x120a4
```
Field offsets in the image: +4..+7 = "MSTC" identity; +9..+12 = MRD (model ID); +0xe..+0x11 = TAG
matches “ModelIdTAGIdentity / ModelIdMRD / ModelIdTAG / ModelIdCustomTAG” log strings 0x24c08-0x24c64.
A valid image matches if its MRD or TAG equals the device NVRAM board-ID string, or its MRD equals
"4506" (legacy board ID).

```
verifyModelId_BRCM(image):                        # called by validateImage for status==2 (whole-flash +flag)
  sysGetNVRAMFromFlash(nvram@fp+0x30)
  sprintf(nvstr, "%02x%02x", nvram[0x2dc], nvram[0x2dd])     # fp+0x460
  sprintf(imgstr, "%02x%02x", image[0x85c], image[0x85d])    # fp+0x450  — image bytes 0x85c/0x85d
  if strcmp(nvstr,"4506")==0  or  strcmp(nvstr,imgstr)==0:
      log(7,..,"Check modelID successfully")                 # else log(3,..,0x24cc0)+return 0x2680
      nvram[0x2dc] = image[0x85c]; nvram[0x2dd] = image[0x85d]   # adopt image board id
      crc = cmsCrc_getCrc32(nvram, 0x400, -1); sysSetNVRAMToFlash(nvram)
      return 0
  return 0x2680
```

### String/constant search results (whole stock-rootfs)
- **"4506"** — libcms_util.so @0x24cb8 (both compare sites above; also check_modelid); wl.ko 2x.
  It is the legacy 4-hex board ID (NVRAM bytes 0x45,0x06) this box migrates to BCD "3300".
- **"63268"** — NOT in httpd/libcms_util. In cferam.000 (43x, CFE banner area "BCM963268",
  "CFE_BOARDNAME") and kernel modules (adsldd.ko, bcmfap.ko, bcm_enet.ko…). It is the SoC chip id:
  verifyBroadcomFileTag requires strtol(image+0x26,16) == devCtl_getChipId() (BCM63268 ⇒ 0x63268).
- **"963168MXH_17A"** — NOT present anywhere in stock-rootfs (nearest CFE table entries:
  "963168MBV_17A", "963168XH", "963168VX", "963268BU"… @cferam.000 0x20bb8+). It is image-side
  content (the ModelIdTAG of real ZyXEL images), not a server-side constant.
- **"MSTC"/"MS"** — libcms_util 0x24c80/0x24c7c (image identity + NVRAM prefix); "MSTC" also appears
  in httpd/cferam/kernel strings as a vendor/board token.
- **NVRAM variable names** — no string-based lookup: the NVRAM is a positional 0x400B struct; fields
  are raw byte offsets (0x2da "MS", 0x2dc/0x2dd board id). sysGetNVRAMFromFlash/sysSetNVRAMToFlash
  are imported from the NVRAM libs (libcms_boardctl.so @0x843/0x858, libcms_core.so @0xa8ee/0xa913).

## 3. httpd upload flow

### 3.1 do_upload_pre_MSTC — httpd 0x4777b4–0x4782dc (the -upload.cgi / -wwanupload.cgi handler)
```
do_upload_pre_MSTC(session, contentLen, type, arg3)      # type: 1=firmware, 2=config restore, 3=WWAN pkg
  log(7,"do_upload_pre_MSTC"@0x4c5280,0x468,"[httpd] upload_pre: content_len=%d upload_type=%d")
  memset(globals@0x4eab5c,0,0x518)
  glbUploadStatus = (u32*0x4e9610) ; glbImgFormat = (u32*0x4e9614)
  if type == 3: ret = upLoadImageFile(session, contentLen, 3, &0x4eab40(filePtr), [sp]=&0x4eab38(imgLen))   # 0x477870-0x47788c
  else:         ret = upLoadImage     (session, contentLen, type, &0x4eab34(imgBuf), [sp]=&0x4eab38(imgLen))   # 0x477890-0x4778a8
  glbUploadStatus = ret                                          # 0x4778b8
  if ret != 0: goto RENDER (0x477e38)                            # 0x4778c4
  log(7,..,"image uploaded, now determine format and validate")  # 0x4778d0-0x4778e8
  printf("Got image via http, total image size: %d\n", imgLen)   # 0x4778f4-0x477904
  if type == 3:                                                   # 0x47790c
      glbImgFormat = zy_WWANPackageCheckDecryption(filePtr, imgLen)   # 0x47791c-0x477928
  else:
      glbImgFormat = cmsImg_validateImage(imgBuf, imgLen, msgHandle, 0)   # 0x477938-0x477950 (a3=0)
      # ---- map validateImage return to an upload status ----
      if glbImgFormat == 3:                        # config file detected
          if type == 2: goto ACCEPT_CONFIG        # 0x477974
          log(3,..,"image mismatch, got config file but user requested flash/broadcom image"@0x4c4dc0)
          glbUploadStatus = 0x267b;    goto RENDER     # 0x4779a0/0x477a64
      elif glbImgFormat != 0:                        # 0x4779a4
          if glbImgFormat == 5:  log(3,..,"invalid image model id [content-len=%d imageLen=%d]");   glbUploadStatus = 0x2680   # 0x477a20-0x477a64 (model mismatch)
          elif glbImgFormat == 6: log(3,..,"invalid image boot rom size [content-len=%d imageLen=%d]"); glbUploadStatus = 0x2681  # 0x477a74 (defensive; validateImage never returns 6)
          elif glbImgFormat == 9: WWAN update path ("update WWAN Package !!\n")                               # 0x477ab8-0x477ad4
          else: goto VALID (0x477c54)               # glbImgFormat ∈ {1,2} → success
      else:  # glbImgFormat == 0 → unknown format
          if type == 3: log(3,..,"invalid wwan package format .."); glbUploadStatus = 0x2682   # 0x4779b4-0x4779e4
          else:         log(3,..,"invalid image format [content-len=%d imageLen=%d]"); glbUploadStatus = 0x267b   # 0x4779ec-0x477a1c
  ACCEPT_CONFIG / VALID: (0x477c54)
  log(7,..,"[httpd] got recognized and valid format %d", glbImgFormat)
  if glbImgFormat == 3:                              # config restore path (type==2)
      ret = cmsImg_procCFGFilter(imgBuf, imgLen, msgHandle, &resp@sp+0x20, &glbWebVar+0x2c8)   # 0x477c88-0x477cb0
      glbUploadStatus = ret; if ret: log(3,..,"process CFG Filter Faile, glbUploadStatus : %d") ; goto RENDER
      ... (responseMsg handling, free image, re-alloc from responseMsg->len, copy)              # 0x477cc8-0x477e08
      goto RENDER
  RENDER: (0x477e38)
  printf(... all the debug lines ...); dumpHex(imgBuf,0x10)/tail
  if type == 1: cmsMem_free(imgBuf); imgBuf=0                     # 0x477fec-0x478034
  if type == 2: cmsFil_removeDir("/fw"@0x4c4a10); fclose(filePtr) # 0x478038-0x478080
  if type == 1 or type == 3: cmsImg_sendLoadDoneMsg(msgHandle)    # 0x478098-0x4780b4
  log(7,..,"[httpd] upload_pre: sending back upload status (%d)", glbUploadStatus)   # 0x4780c4
  makePathToWebPage("pages/tabFW/tabFW.html"@0x4d187c); do_ej(...)                  # 0x4780f0-0x478150
  if glbUploadStatus == 0: globType@0x4eab30 = type; glbWebVar+0x10c28 = (type==3 ? 0 : 1)  (0x478128: lui v1,1; addu v0,glbWebVar,v1; sw @0xc28(v0))
  return
```
**Failure→glbUploadStatus mapping (0x4e9610):**
| glbUploadStatus | meaning / log string | GUI msg |
|---|---|---|
| 0 | OK — page renders, JS proceeds to firmwareUpgrade-uploadpost.cgi (do_upload_post) | success |
| 0x267b (9851) | invalid image format / config-vs-firmware mismatch / does-not-fit / WWAN decode fail | 3 illegal image |
| 0x2680 (9856) | invalid image model id (validateImage returned 5) | 4 illegal model id |
| 0x2681 (9857) | invalid image boot rom size (validateImage returned 6; branch present but 6 is not produced by current libcms) | 5 illegal boot rom size |
| 0x2682 (9858) | invalid wwan package format | 6 WWAN package fail |
| 0x232c (9004) | allocation failure | 1 out of memory |
| 0x267a (009 934… 0x267a=9850) | "No filename selected" (from upLoadImageFile) | 2 no file selected |
| procCFGFilter ret / 0x2332 etc. | config filter failure / boundary errors | 8 fatal (fallthrough) |

(The page displays the index via `idxStr = '<%ejGetOther(sysInfo, upldSts)%>'` — firmwareUpgrade.html
msg array 1..8; the numeric →idx translation layer lives in the sysInfo EJ table inside httpd.

### 3.2 upLoadImage — httpd 0x476ef4–0x4776f8 (type 1 = firmware, type 2 = config restore)
In-memory upload; **no temp file**.
```
upLoadImage(session, contentLen, type, &imgBuf(0x4eab34), [sp]=&imgLen(0x4eab38)):
  imgBuf=0; imgLen=0
  read 0x100-byte header line (helper 0x476054) into filename@sp+0x2c
  strncpy(glob@0x4eab5c, filename, 0xff)                     # header line 1
  boundary = strstr(filename, glbBoundary@0x4eb1e0); if !boundary: log "mismatch between header boundary and start boundary" → ret 0x2332
  parse "filename="@0x4a75dc marker, CR/LF handling          # “No filename selected” → 0x267a
  read 0x400 chunk; strncpy(glob+0x100, chunk, 0x1ff)        # header line 2
  imageSize = contentLen - headerLen(0x530(sp))
  if cmsImg_willFitInFlash(imageSize) == 0:                  # 0x477270-0x477284 (->0x4a2d70)
      log(3,"upLoadImage"@0x4c5300,0x1ae,"Image of %d bytes will not fit in flash"@0x4c4968)
      return 0x267b
  if imageSize < 0x800 (2048) && type == 1:                  # 0x4772b4
      log(3,..,"Wrong file or illegal size, uploadBufLen=%d type=%d"@0x4c4990); return 0x267b
  globUploadBufLen@0x4eb05c = imageSize ; log(5,..,"upload start with len = %d")
  if type == 1: cmsImg_sendLoadStartingMsg(msgHandle, &requestJSONFlag@0x4e9658)   # 0x47733c-0x47734c
  printf("Allocating %d byte buffer to hold image.\n")
  imgBuf = cmsMem_alloc(imageSize); if !imgBuf: log "Failed to allocate memory for the image. Size required %d"; return 0x232c
  memset(imgBuf,0,imageSize); *s7(imgBuf out) = imgBuf
  # streaming copy loop: read session bytes (fgetc / __fgetc_unlocked / 0x476190 0x2000-chunk reader),
  # store into imgBuf, stop at trailing multipart boundary; “more bytes uploaded than allocated buf” → 0x267b;
  # "final image uploadSize=%d, imageLen=%d result=%d" → imgLen = (boundary_ptr - imgBuf) - 2       # 0x4775d0-0x4775e8
  glob@0x4eab5c+0x504 = uploadSize; glob+0x50c = sleepCount   # 0x4776b8-0x4776c0
  return 0 on success (s1=0), else 0x267b/0x232c
```

### 3.3 upLoadImageFile — httpd 0x4762b8–0x476ef4 (type 3 = WWAN package)
Same multipart parsing as upLoadImage, but saves to disk:
```
upLoadImageFile(session, contentLen, type=3, &fileOut(0x4eab40), [sp]=&imgLen(0x4eab38)):
  ... same boundary/filename parsing (0x267a “No filename selected”, 0x267b size/type errors) ...
  imageSize = contentLen - headerLen
  if cmsImg_willFitInFlash(imageSize) == 0: log "Image of %d bytes will not fit in flash"; return 0x267b   # 0x476640
  cmsImg_sendLoadStartingMsg(msgHandle, &requestJSONFlag)      # 0x476710
  cmsFil_removeDir("/var/fw"@0x4c4a0c)                        # 0x47678c
  cmsFil_makeDir("/var/fw")                                   # 0x4767d4
  snprintf(path, 0x3f, "%s/%s"@0x4cb054, "/var/fw", "ras.bin"@0x4c4a58)     # 0x476830
  fp = fopen(path, "w+"@0x4c4a60)                             # 0x476854
  ... fwrite loop (0x476960/0x476b30) ...
  fclose(fp)                                                  # 0x476cd4
  if type == 3:
      snprintf(path2, 0x3f, "%s/%s", "/var/wwan"@0x4c4bc4, "tmp_wwanpackage"@0x4c4bd0)   # 0x476cf8
      truncate(path2, imgLen-2)                               # 0x476d24
      fp2 = fopen(path2, "r+"@0x4a4c24)                       # 0x476d40
      *fileOut = fp2                                          # 0x476d50 (sw v0,(a0) a0=0x5bc(sp) saved a3)
      imgLen stored via [sp]
  return 0 (errors: 0x2682 dir/file-create fail, 0x267b read fail, 0x265a …)
```
**Exact file artifacts: `/var/fw/ras.bin` (upload staging), then `/var/wwan/tmp_wwanpackage`**
(truncated to image length, opened "r+") handed to zy_WWANPackageCheckDecryption → zy_updateWWANPackage
(“update WWAN Package !!\n”). The firmware/config images never touch disk.

### 3.4 do_upload_post — httpd 0x475e30–0x476054 (firmwareUpgrade-uploadpost.cgi)
```
do_upload_post():
  if glbImgFormat == 9: return                                # WWAN magic number
  log(5,"do_upload_post"@0x4c5270,0x58b,"Calling cmsImg_write image now"@0x4c46f0)
  if globType@0x4eab50 == 2: zyLog_cfg(0x1d,"System Reboot Due To Restoring Configuration(GUI)"@0x4c4710)
  elif == 1:                  zyLog_cfg(0x1d,"Firmware Upgrading. System Reboot Will Wait For a Few Minutes(GUI)"@0x4c4744)
  if glbImgFormat == 1 or glbImgFormat == 2:                  # 0x475ec4-0x475ed0 (addiu -1; sltiu 2)
      devCtl_setImageState(0x30)                              # 0x475ed8-0x475edc (0x30=48 IMAGE_STATE)
      ret = cmsImg_writeImage(imgBuf@0x4eab34, imgLen@0x4eab38, msgHandle@0x4e9640)   # 0x475ef8-0x475f00
      # cmsImg_writeImage (libc 0x13550): r=cmsImg_validateImage(buf,len,msg,0);
      #   r==0 → return 0x267b (reject), else cmsImg_writeValidatedImage(buf,len,r,msg)
      # writeValidatedImage dispatch: fmt 1/2 → per-partition writer 0x128f4 (flashes CFE/kernel/rootfs via
      #   devCtl_boardIoctl, strings "cfeSize=%d kernelSize=%d rootfsSize=%d"/"Flashing CFE..."@0x24fb8/0x24fe0)
      #   fmt 7 → sendConfigMsg(..,0x10000876); fmt 3 → sendConfigMsg(..,0x10000875); ok → cmsUtil_sendRequestRebootMsg(msg)
      if ret == 0:
          log(5,..,"[httpd] flash image complete, ret=%d"); if getWebStyleType()==1: cmsMem_free(imgBuf); imgBuf=0
      else:
          log(5,..,"flash image failed, ret=%d"); return       # 0x475f58-0x475f78 → NO reboot
  # success path:
  if globRestoreFlag@0x4eab3c (s1=a3 stored in memset delay-slot @0x477840, v0=0x4f0000) != 0:                           # 0x475f94
      log(5,..,"[httpd] cgi upload, restore default")
      cmsLck_acquireLockWithTimeoutTraced(...); zyLog_cfg(0x1d,"System Reboot Due To Back to Factory Defaults(GUI)"@0x4a78e4)
      cmsMgm_invalidateConfigFlash(); cmsLck_releaseLockTraced(...)
  if glbImgFormat == 0xa: return
  cmsUtil_sendRequestRebootMsg(msgHandle)                     # 0x476028-0x476040 → reboot & boot new image
```
Success chain: **devCtl_setImageState(0x30) → cmsImg_writeImage → (validate again → writeValidatedImage
→ devCtl_boardIoctl partition flashes / CMS 0x10000876) → cmsUtil_sendRequestRebootMsg**; reboot message
is sent even for the config-restore path (glbImgFormat==3 handled earlier in do_upload_pre; here
glbImgFormat 1/2 get writeImage, anything else skips straight to reboot/invalidate).

## 4. Format branching — config vs firmware, magics

- Config-file detection is **content-based**: `cmsImg_isConfigFileLikely` (0x133ec) requires the file to
  start with **"<?xml version"** (0x25114) and contain **"<DslCpeConfig"** (0x25124) within offsets
  0x14..0x31; then validateImage validates it by sending it to the config daemon (sendConfigMsg cmd
  0x10000873) and returns 3 = "config format verified". httpd's *"image mismatch, got config file but
  user requested flash/broadcom image"* (0x4c4dc0) fires when glbImgFormat==3 and type!=2
  (0x477968-0x4779a0) → glbUploadStatus 0x267b (GUI "illegal image"). type==2 (chkRestoreDefault →
  firmwareUpgrade-upload-restore.cgi) accepts it and runs cmsImg_procCFGFilter (0x477ca0).
- Firmware detection does **NOT** test JFFS2 magic 0x1985, SquashFS magic, or any uImage magic —
  the byte sequences 0x19 0x85 appear nowhere in httpd or libcms_util.so. There is no "FILE_TAG"
  concept ("FileTag" substring only exists inside the function name "verifyBroadcomFileTag" @0x257d0).
- Firmware branching inside validateImage is instead:
  1. verifyBroadcomFileTag (tag-format: token CRC over first 0xec bytes == BE32 at +0xec; payload
     `crc32(image+0x20000, atoi(image+0x3e), 0xFFFFFFFF)` == BE32 at +0xd8; tag version byte0 == '6';
     chip id strtol(image+0x26,16) == devCtl_getChipId (63268)) → status 1; or
  2. the trailing-20-byte CRC whole-flash fallback → status 0/2 and (web) rejection;
  3. plus size gates: imageLen ≤ getImageFlashSize()+20 (tag path) / ≤ getImageFlashSize() (whole-flash),
     and httpd-level imageSize+0x100 < getImageFlashSize() (cmsImg_willFitInFlash 0x13294) and
     imageSize ≥ 2048 for type 1 (0x4772b4).

## 5. Definitive recipe for a self-made firmware .bin (server-side checks)

To pass ALL web-upload server checks (SBG3300-N000, BCM63268), the file must be a "Broadcom-tag"
image (status 1 path; the only class the web path accepts):

Header (0..0xeb, 236 bytes) + token CRC:
- byte 0 = ASCII `'6'` (tag version; atoi(image)==6) — verifyBroadcomFileTag 0x12768-0x127b0.
- offset 0x18 / 0x26: chip-id ASCII-hex string at **0x26**; `strtol(image+0x26,NULL,16) ==
  devCtl_getChipId()` (0x63268 for BCM63268) — matchChipId 0x11bf0 via 0x1283c; the value at 0x18 is
  not compared (passed as unused a1).
- offset 0x3e: ASCII decimal total payload length (atoi → totalImageLen) — 0x1261c.
- offset 0xd8: BE32 imageCrc = `crc32_raw(image+0x20000 .. +0x20000+totalImageLen, seed 0xFFFFFFFF)`
  (table CRC-32 IEEE, no final XOR) — 0x12674-0x126b8.
- offset 0xec: BE32 tokenCrc = `crc32_raw(image[0..0xeb], 0xFFFFFFFF)` — 0x12544-0x12574.
- offset 4..7: **"MSTC"** and NVRAM[0x2da..0x2db] must be **"MS"** (factory-set) — verifyModelId_MSTC 0x11f70/0x11f9c.
- offsets 9..12 (MRD) and 0xe..17 (TAG): MRD or TAG field must equal the NVRAM board-id string
  (`"%02x%02x"` of NVRAM[0x2dc,0x2dd]) OR MRD must equal `"4506"` — verifyModelId_MSTC 0x11ff4-0x1207c.
- whole file size: `imageSize ≥ 2048` (httpd 0x4772b4, type1) AND
  `imageSize + 0x100 < cmsImg_getImageFlashSize()` (willFitInFlash 0x13294 via 0x477270) AND
  in-lib re-check `imageSize ≤ getImageFlashSize() + 0x14` (0x141b4-0x141f4).
- model id string "4506"/board values and chip value 63268 are the only server constants; "963168MXH_17A"
  is not checked anywhere (image-side tag content only).

Then validateImage returns 1 → glbUploadStatus 0 → do_upload_post → cmsImg_writeImage re-validates
(must be ≠ 0) → cmsImg_writeValidatedImage flashes CFE/kernel/rootfs partitions via devCtl_boardIoctl
and CMS messages → cmsUtil_sendRequestRebootMsg → reboot.

What remains kernel/CFE-side only (NOT verified in userspace):
- CFE (cferam.000) boot-time checks: JFFS2 rootfs containing `vmlinux.lz`
  ("ERROR: A JFFS2 directory entry for %s was not found." @cferam 0x1ed15), kernel decompression
  ("Decompression OK!", "Entry at 0x%p"), CFE_BOARDNAME/CFE_VERSION tables ("BCM963268" @0x20ba1).
- Linux kernel: vmlinux.lz decompression, uImage/rootfs mount integrity — none of these have any
  counterpart in httpd/libcms_util; a .bin that passes the userspace checks but contains garbage
  kernel/rootfs will still fail at CFE/kernel boot.

### HTTP-upload-to-flash chain (vaddr evidence per step)
1. firmwareUpgrade.html posts multipart (file input "filename", .bin) to
   /pages/tabFW/firmwareUpgrade-upload.cgi (or -upload-restore.cgi with chkRestoreDefault).
2. httpd dispatches to `do_upload_pre_MSTC` 0x4777b4 → `upLoadImage` 0x476ef4 (type 1/2, RAM buffer
   imgBuf@0x4eab34/imgLen@0x4eab38; type 3 → `upLoadImageFile` 0x4762b8 → /var/fw/ras.bin +
   /var/wwan/tmp_wwanpackage@0x4c4bd0/0x4c4bd0).
3. Size gate: cmsImg_willFitInFlash 0x477278 (import 0x4a2d70; impl libc 0x13294).
4. Progress msg: cmsImg_sendLoadStartingMsg 0x477340 (import 0x4a42e0).
5. Classification: cmsImg_validateImage 0x477948 (import 0x4a3f80; impl libc 0x14000) with
   a0=imgBuf, a1=imgLen, a2=msgHandle, a3=0 → glbImgFormat@0x4e9614; status mapping → glbUploadStatus@0x4e9610 (0x477958-0x477e34).
6. Config restore: cmsImg_procCFGFilter 0x477ca0 (import 0x4a36f0); done msg cmsImg_sendLoadDoneMsg 0x4780b0 (import 0x4a2330); page render makePathToWebPage("pages/tabFW/tabFW.html") 0x4780f0 + do_ej 0x478148.
7. JS → firmwareUpgrade-uploadpost.cgi → `do_upload_post` 0x475e30: devCtl_setImageState(0x30) 0x475ed8 → cmsImg_writeImage 0x475ef8 (import 0x4a3f10; impl libc 0x13550: re-validate 0x1358c, then writeValidatedImage 0x136d4) → partition flash via devCtl_boardIoctl 0x129f4 / sendConfigMsg cmd 0x10000876 0x13818 → cmsUtil_sendRequestRebootMsg 0x47602c (impl libc 0x14964) → reboot.