# Offline boot artifact audit

The current initramfs ELF is MIPS big-endian. Its unwrapped kernel blob contains
an embedded newc CPIO archive. The parser `tools/audit-initramfs.py` is strictly
read-only and finds 761 records through `TRAILER!!!`, including `init`,
`sbin/init`, `bin/busybox`, `etc/preinit`, and `sbin/procd`. Its focused tests
pass 2/2.

This verifies only the CPIO archive is embedded with expected OpenWrt init
files. It does not verify that the SBG3300 CFE can load this ELF, that the entry
address/DTB handoff/memory map is correct, or that it boots on hardware.

The broad test discovery currently fails at a separate unfinished test
`tests/test_nand_slot_math.py`, which imports `tools/sbg3300-slot-map.py`; that
tool does not exist and was not created. Do not treat the full suite as passing.
