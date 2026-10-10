# Original PTM netdev/NAPI component — offline build milestone

Evidence: `FAMILY-SOURCE`, `UPSTREAM`, `BUILD-RESULT`; runtime `NOT-TESTED`.
OpenWrt pin `5edcc1c43cb97048b506168fbbe00538956796d6`, preserved profile
checkout `18c17336871e73ddfbab3198104d8c42df844146`, Linux 6.18.54.

## Implemented source

`drivers/xtm/xtm_ptm.[ch]` implements a single unbonded PTM netdev using the
existing real DMA adapter: IRQ status/masking/acknowledgment, NAPI, TX BQL and
backpressure, RX refill work and Ethernet dispatch, link events, statistics,
MAC acquisition through `device_get_ethdev_address`, and resource teardown.
`xtm_ptm_core.[ch]` validates match IDs, SOP/EOP, cells/errors, trailer bounds,
and the family's PTM TX descriptor status. Tests use this actual shared core.
No fabricated legacy export, FKB classification, firmware or vendor body is used.

The ISR masks sources but does not acknowledge behind a scheduled poll; NAPI
acknowledges before consuming so late completions remain pending on unmask.
Budget-zero polling only consumes TX. Empty RX rings mask interrupts until
refill work reschedules NAPI. Failed channel halt quarantines the ring/mappings;
the parent must retain the netdev and all controller resources until successful
unregister. This path needs later fault-injection/runtime validation.

## Exact contract provenance

The inspected family tree is `bcm963xx_4.12L.06B_consumer` at
`e2f23ddbb20bf75689372b6e6a5a0dc613f6e313`, read locally only.
`bcmdrivers/opensource/net/xtmrt/impl4/bcmxtmrt.c` lines 1285–1323 supply the
PTM TX status contract; lines 1913–2035 supply RX match/error/cell/trailer
handling. `bcmxtmrtimpl.h` lines 105–125 define status facts;
`bcmxtmrtbond.h` defines the 2-byte PTM CRC. These factual contracts are
independently implemented using Linux 6.18 APIs, with explicit caller inputs
rather than guessing the DSL-configured VCID or trailer-removal state.

## Build results

Two fresh external build directories, `run-ZG1LGA` and `run-82hkqS`, under
`~/.cache/sbg3300-xtm-runtime/`, produced identical module bytes with normalized
debug source paths. Compiler/modpost exits 0, W=1 plus -Werror, no compiler
warnings. Both use the preserved kernel .config/Module.symvers/vmlinux/UTS
inputs and confirm their hashes unchanged. Full compiler commands/logs,
source hashes and symbol inventories remain local in each run directory.

- Module: `sbg3300_xtm_dma.ko` (ring plus PTM frontend).
- SHA256: `44e54b9388521052bd0fbb4f9b4994b3c4f8e5296ffc0c2ec533ffc889dca95e`.
- ELF: 32-bit, big endian, MIPS/o32.
- Vermagic: `6.18.54 SMP mod_unload BMIPS 32BIT`.
- Imports: 65, all present in the preserved kernel exports; missing 0.
- Native and Clang ASan/UBSan ring/PTM tests pass.
- Earlier candidate directories are retained as intermediate evidence.

## Explicit integration boundary

This module exports a frontend constructor; it does not automatically bind
hardware or enable a DTS node. The constructor requires an already exclusively
owned and initialized SAR controller, verified DMA window, mapped channel/state
resources, translated Linux IRQs, real platform MAC, and DSL configuration.
The exact-family SAR DMA base/channels/interrupt IDs are contract facts, but
safe global SAR/PHY/FAP ownership and reset sequencing remain unresolved.
No guessed platform probe, clock/reset sequence, carrier event or working DSL
sync is supplied. ATM cells are rejected by this PTM path; ATM/bonding/control
requires a separate established contract. Link-update callers must be sleepable
and must not already hold RTNL. Parent lifetime must serialize all exported APIs.

The inherited probe remains **unlinked with 19 imports**, separately from stock
`adsldd.ko` (82) and `bcmxtmcfg.ko` (31). This new component does not resolve or
relink that legacy module. No device has been accessed or module loaded.
