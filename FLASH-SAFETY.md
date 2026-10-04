# Flash safety gates

Every image produced before gate completion must be named and labeled
`OFFLINE-ONLY` / `NOT-FLASHABLE`.

The current SBG3300 artifact is an OpenWrt initramfs loader ELF. It is not a
Zyxel/Broadcom stock firmware container and is not proven loadable by this
device's CFE or stock updater. A successful build is not a boot or recovery
test. The DTB has no selected UART console, and this project does not use
UART/JTAG.

No upload or flash may occur in this R&D task. A future `READY-FOR-CONTROLLED-
FLASH` decision requires, at minimum:

- complete physical NAND layout including CFE, firmware, data, NVRAM, reserved
  regions, ECC/OOB and bad-block handling;
- correct stock-container semantics, board/chip validation and image lengths;
- proven Ethernet/DSA topology and a usable non-UART recovery route;
- exact stock fallback images verified and preserved;
- initramfs validation and full offline image inspection;
- all project gates in `PLAN.md` and `STATUS.md` passed with evidence.

Even after those gates, stop for explicit user authorization. Never use raw
MTD writes, CFE changes, factory reset, or blind trial flashing.
