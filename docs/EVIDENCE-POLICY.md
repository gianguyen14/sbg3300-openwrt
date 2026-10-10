# Evidence and confidence policy

Use one or more of these labels with every material hardware/software claim:

| Label | Meaning |
|---|---|
| `LIVE-DEVICE` | Direct observation from the SBG3300 running stock firmware; identify the report/source and date. It does not establish OpenWrt behavior. |
| `STOCK-BINARY` | Static inspection of a binary extracted locally from the stock firmware; do not redistribute the binary. |
| `STOCK-BOOT-LOG` | Boot/kernel log or stock boot output from this device. |
| `EXACT-BOARD-SOURCE` | Source contains the exact `963168MXH_17A` board entry. Build lineage equivalence may still be uncertain. |
| `FAMILY-SOURCE` | Source for a related BCM63168/Broadcom family, not proven to be the running Zyxel build. |
| `PRODUCT-DOCUMENTATION` | Manufacturer product documentation describes intended product ports/features; it does not map those ports to SoC, switch, or PHY indices. |
| `UPSTREAM` | Behavior/code in a named, pinned Linux/OpenWrt revision. It establishes upstream implementation only. |
| `BUILD-RESULT` | A command completed for a named source/config/target. It establishes compilation/artifact generation only. |
| `INFERENCE` | A conclusion derived from evidence. State assumptions and confidence. |
| `UNKNOWN` | Evidence is insufficient or conflicting. |

Keep separate columns or sentences for build and runtime state. Use `NEEDS-DEVICE`
for physical tests that cannot be established offline. Avoid unqualified words
such as “supported,” “works,” or “confirmed” when only family source or a build
is available.

Examples:

- BCM63168D0 silicon ID: `LIVE-DEVICE` / `STOCK-BOOT-LOG`.
- Boardparms contains `963168MXH_17A`: `EXACT-BOARD-SOURCE`; whether that source
  is byte-for-byte the running 2018 build remains unproven.
- `b53_spi` matches `brcm,bcm53125`: `UPSTREAM`; actual SBG3300 switch silicon
  and wiring remain `UNKNOWN`.
- SBG3300 initramfs build exits zero: `BUILD-RESULT`; SBG3300 boot remains
  `UNKNOWN`.
- The 4.12L.06B dual-slot model aligns with the observed rootfs MTD start:
  `FAMILY-SOURCE` plus `INFERENCE`; exact writer semantics remain unresolved.
