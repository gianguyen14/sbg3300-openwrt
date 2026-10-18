# Live modem checks — web-update acceptance (READ-ONLY)

Run on the machine that has the `sbg3300` wrapper (Expect+SSH to the SBG3300).
All commands read-only. Paste back ONLY selected facts (no MACs, no NVRAM
dumps, no credentials, no serials). Raw output should stay out of Git
($HOME/.cache/sbg3300-readonly-YYYYMMDD/, mode 0700).

## What these checks will decide

The web-update validator (reverse-engineered from stock firmware, verified
against `V1.01(AADY.9)C0.bin`, see reports/UPGRADE-RECIPE.md) compares the
uploaded image tag against the LIVE unit:

- tag family field "+0x09" vs NVRAM model id
- tag model field "+0x0e" vs NVRAM model id ("4506" or NVRAM value)
- tag chip field "+0x26" hex vs devCtl_getChipId() (0x63268 = BCM63168)
- size: imageLen+0x100 < flash size; imageLen >= 0x800
- header/payload CRCs (crc32 seed 0xFFFFFFFF, no final xor)

Pending unknowns on the live unit:

1. NVRAM variable names + current model id value (4506 vs migrated 3300):
   nvram show | grep -iE 'model|board|chip|mrd'
   (report ONLY variable names and model-id values; redact any MAC/secret)

2. Kernel compile flags for the MSTC/ZyXEL image-update path:
   grep -iE 'fwup|mstc|rom.?d|obm' /proc/kallsyms | head -n 40
   cat /proc/brcm/kernel_config
   grep -iE 'fwup|mstc|dual|image' /proc/brcm/kernel_config

3. MTD layout (rootfs_update / dual-image slot presence):
   cat /proc/mtd | sed 's/0x[0-9a-fA-F]*/SIZE/'
   (report eraseblock sizes + partition names only, NOT contents)

4. Live chip/board identity:
   cat /proc/cpuinfo | grep -iE 'model|system|machine'
   cat /proc/device-tree/model 2>/dev/null
   nvram get chipid 2>/dev/null; nvram get boardid 2>/dev/null

5. Upload staging paths (existence only):
   ls -ld /var/fw /var/wwan 2>/dev/null

6. Running web app confirms the binaries analyzed are the ones in flash:
   cat /proc/version
   ps | grep -E 'httpd|cms' | grep -v grep

## Output format to send back

Plain text lines like:
MODELID=4506        (or 3300)
CHIPID=63268
BOARDID=963168MXH_17A
MTD=rootfs:0x16a0000,data:0x400000,nvram:0x20000,erase:0x20000
KERNELCONFIG_FWUP=y/n/missing
PROC_VERSION=...