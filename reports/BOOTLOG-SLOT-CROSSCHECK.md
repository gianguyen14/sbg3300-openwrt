# Public bootlog vs stock tag: slot-address cross-check (offline)

Source bootlog: `/home/hermes/sbg3300-openwrt/research/bootlog1.html`, public
2016 same-board example. It reports Boot image choice `0` (latest), CFE latest
image address `0xb8040000`, kernel command line `root=mtd:rootfs ...`, and rootfs
MTD offset `0x00040000`. It is not a readout from the owner's 2018 live router.

The stock download tag says `rootfsAddress=0xbfc40000`; family vendor formula
with `IMAGE_BASE=0xbfc00000`, `FLASH_BASE=0xb8000000`, 32-bit `BOOT_OFFSET`
translates that to MTD offset `0x00040000`. Thus the public bootlog's MTD start
matches the stock file tag after address translation; this is evidence for the
slot-1 template on that public example, not the live router's current slot.

The family writer can choose an inactive slot at half flash plus 128 KiB. For
128 MiB flash that yields `0x04020000`; this matches the separately reported
2018 owner MTD start, but those two sources are different evidence periods.
No 2018 active tag, sequence/bootline, bad-block offset or exact source-build
binding has been verified. Do not call the owner router slot 2 from this
coincidence alone.

Repro tool: `tools/audit-stock-bootlog-slot.py`; it compares the stock tag to
the public bootlog and labels the bootlog evidence scope. It does not read the
router, infer filesystem contents, or authorize DTS changes or image writing.

No DTS/image changes; no device actions. `NOT-FLASHABLE` remains.
