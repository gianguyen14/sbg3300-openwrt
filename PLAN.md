# Work plan and evidence gates

## Phases

1. Freeze stock-custom stable artifacts and capture read-only router evidence.
2. Pin official OpenWrt upstream; inspect `bmips/bcm63268` and build it
   unmodified.
3. Recover stock kernel/module/board-parameter evidence.
4. Establish SoC, RAM, NAND ECC, physical NAND map, MAC source and Ethernet path.
5. Draft a minimal evidence-backed DTS and offline device definition.
6. Identify the WLAN chipset/calibration arrangement and evaluate drivers.
7. Map proprietary DSL/XTM source lineage and attempt an explicit forward-port.
8. Build offline images and validate their format without installing them.
9. Decide whether the no-UART recovery and stock updater make first installation
   acceptably recoverable. Stop if evidence is incomplete.

## Promotion rules

- Upstream build success does not imply SBG3300 support.
- DTS compilation does not imply correct hardware description.
- Kernel/module compilation does not imply DSL sync or switch operation.
- A stock image validator PASS does not prove NAND layout safety.
- `READY-FOR-CONTROLLED-FLASH` still requires an explicit user authorization;
  this project never auto-flashes.

## Current blockers

- Full physical NAND map and bad-block/CFE boundaries are not proven.
- Exact BCM53125 presence and MDIO/RGMII/CPU-port wiring are not established.
- Broadcom vendor DSL source availability and match to stock modules are
  unresolved.
- The research-only SBG3300 initramfs profile now builds offline, but no
  stock-compatible image wrapper or CFE handoff has been proven.
- Recovery reachability is not currently proven/tested for this exact board.
