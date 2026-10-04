# BCM63168 XTM compile probe against OpenWrt 6.18

Date: 2026-10-04

## Scope

This was a host-side cross-compile probe of the public 4.12L.06B
`bcmxtmrt.c` implementation against the already configured OpenWrt bmips
Linux 6.18.54 headers and MIPS32/o32 toolchain. Sources were symlinked into an
isolated `/tmp` external-module directory; no files in the vendor checkout or
router were changed. No output module linked or loaded.

The source is not self-contained: it depends on vendor `blog`/NBuff, packet
DMA, FAP/BPM/IQoS, XTM config, board, and Broadcom glue interfaces. The first
probe omitted the vendor include due to the project path containing spaces and
stopped at `linux/blog.h`; this was a harness setup error and is not counted as
a driver result. The retry used a space-free temporary symlink and proceeded
further.

## Compatibility probe findings

The source reaches vendor headers after supplying a temporary header mapping
legacy `linux/autoconf.h` to the current generated config. Compilation then
stops before code generation completes with:

- Missing legacy NBuff types/fields: `RecycleFuncP` and
  `sk_buff.recycle_flags`.
- Vendor packet-DMA types not resolved through the current module build:
  `DmaChannelCfg`, `DmaDesc`, and `DmaRegs`.
- Removed kernel include: `asm/system.h` from vendor `bcm_OS_Deps.h`.

Logs:

- `/tmp/sbg3300-xtm-module-build-2.log`: failed early from the space-containing
  include path; discarded.
- `/tmp/sbg3300-xtm-module-build-3.log`: valid compatibility probe; records the
  missing legacy ABI/types above.

## Interpretation

The available XTM implementation cannot be dropped into Linux 6.18 as-is. The
NBuff recycle model and Broadcom DMA data path are structural dependencies, so
this needs an intentional compatibility/driver redesign, not just renaming a
few Linux APIs. The compile probe has not established whether those components
can be ported safely.

The inspected tree still lacks the Makefile inputs `adsldd$(PROFILE).o_save`,
`bcmxtmcfg$(PROFILE).o_save`, and `adsl_phy$(PROFILE).bin_save`. Stock
`adsldd.ko` and `bcmxtmcfg.ko` are 2.6.30 MIPS relocatables and are not valid
Linux 6.18 modules. Therefore a complete DSL path remains source-incomplete:
PHY control, XTM configuration, and a buildable data path all need resolution.

No hardware runtime claim is made. In particular, neither DSL sync nor
PPPoE-over-XTM has been tested under OpenWrt.
