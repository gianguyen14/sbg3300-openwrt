# Real XTM ring/DMA component — Linux 6.18.54

Evidence label: `BUILD-RESULT`, 2026-10-10. The implementation is in
`drivers/xtm/xtm_core.c` and `drivers/xtm/xtm_dma.c`, with their headers/Kbuild.
This is real runtime component code using Linux APIs; it has no probe shims,
vendor compatibility headers, dummy imports, or module initialization touching
hardware. It is not yet integrated with a platform driver, IRQ/NAPI, netdev,
or the DSL control plane.

## Canonical inputs and preservation

- OpenWrt base: `5edcc1c43cb97048b506168fbbe00538956796d6`.
- Existing approved offline profile checkout:
  `18c17336871e73ddfbab3198104d8c42df844146`, descending from that base.
- Kernel: 6.18.54; BMIPS4350-capable, big-endian, 32-bit, SMP,
  `CONFIG_DMA_NONCOHERENT=y`, modules enabled, modversions disabled.
- Compiler: OpenWrt GCC 14.4.0, `r0-5edcc1c`.
- Kernel config SHA256:
  `adff90c129b8dbbfd4e5efc5603553cf9b02b460e07c786fcce5981622e30446`.
- Kernel `Module.symvers` SHA256:
  `1b3be3d551a9e469aefd5658536020a0503e59fbdb4e9809fa4bb97bfe134d90`.
- Existing local `vmlinux` SHA256:
  `fdda1a944e9511d082170ede37fecdc970af6cf8efc81bf08150ad340552b2e8`.

The script snapshots `.config`, `Module.symvers`, `vmlinux`, and UTS release
before/after the external build and requires exact equality. It uses a fresh
external directory on each invocation. Kernel inputs and both source mirrors
remained unchanged. No kernel rebuild, install, device access or module loading
was performed. These local build hashes are separate from the inherited Hermes
build hashes.

## Compiler and modpost

Command: `bash tools/build-xtm-dma.sh`, which runs external Kbuild with
`ARCH=mips`, the matching cross compiler, `W=1 KCFLAGS=-Werror V=1`.
Final run directory: `${XTM_BUILD_ROOT}/run-RAhjKP`; default evidence root is
`$HOME/.cache/sbg3300-xtm-runtime`.

- Complete compiler/modpost log: `compiler-modpost.log`, 34 lines, SHA256
  `8a8e0819e547f9d1eeaa1908d033a93dedeeb64af17892e772faceac18e0f515`.
- Source-input hash manifest: `source-inputs.json`, SHA256
  `2d1ab2780d11002e026f6b8d424375b907fa864eb480fa7a9a1dda2c23bd95d1`.
- Compiler/modpost exit: **0**; final log has no warning/error diagnostics.
- Artifact: `module/sbg3300_xtm_dma.ko`, **64,616 bytes**.
- Module SHA256:
  `e613ad71903b82dbe363a500ce2292b9ba8ea82f7de28a23158fa6c22abeaa40`.
- ELF: ELF32, big-endian, relocatable MIPS, o32/mips32 flags.
- Vermagic: `6.18.54 SMP mod_unload BMIPS 32BIT`.
- 24 imports, all present in the pinned kernel's exports; zero missing imports.
  The exported `xtm_dma_*` APIs are actual implementations, not renamed stubs.

The initial builds/logs are preserved in `run-OWQx10` and `run-WTJuKm`.
They linked but reported missing OpenWrt `STAGING_DIR` and stripped module
description metadata. The build tool now sets the real staging path; the source
explicitly retains its description with `MODULE_INFO` because this unchanged
OpenWrt config sets `CONFIG_MODULE_STRIPPED=y`. No modpost/ compiler warning
heuristic was disabled. An intermediate corrected build is in `run-IXclcc`.

## Tests and supported behavior

The same ring-policy C code runs in native host tests and the kernel component.
Native `-Wall -Wextra -Werror` tests and Clang ASan/UBSan tests passed. They test
descriptor bit encoding and boundary length, full/empty and single-entry rings,
non-power-of-two wrap/FIFO over 10,000 steps, ownership refusal, raw SAR status
preservation, malformed RX lengths/error status, and full-ring cancellation
after simulated controller quiescence. Four existing Python image-parser tests
also pass. GCC sanitizer linking initially lacked host ASan/UBSan libraries;
Clang supplied the sanitizer run without changing dependencies.

DMA adapter behavior includes coherent ring allocation, copied linear TX
buffers, separately allocated RX buffers, DMA mapping-error/range checks,
`dma_wmb` before ownership publication, `dma_rmb` after observed completion,
unmapping before CPU access, real statistics and bounded channel stop.
Mapping/allocation failures unwind their resources. Stop timeout blocks new
submissions and preserves mappings; destruction rejects a running/ enabled
channel. Channel stop is terminal; a new session allocates a new ring.

These tests do not execute Linux DMA mapping or MMIO against hardware. The
allocation/mapping/timeout branches are compiled and reviewed, not physically
validated.

## Integration status and exact blockers

The 19-import Hermes diagnostic remains a different module build. It has not
been relinked against this API: **all 19 legacy imports remain unresolved in
that inventory**. No fake functions with the legacy names were exported.

Before a full runtime candidate can be built/enabled:

1. Integrate an actual platform/netdev/NAPI frontend with these ring APIs,
   including transport-specific FSTAT, encapsulation, cell/match-ID dispatch,
   RX refill, TX backpressure and network statistics.
2. Establish global SAR clock/reset, controller setup and exclusive host DMA
   ownership versus stock FAP/SW-DMA. The channel helper only programs an
   already-owned inactive channel; it does not initialize the global SAR.
3. Provide exact platform resources/DT binding. Exact-family and pinned
   upstream evidence agree on RX0/1 hwirqs 26/27. Legacy IRQ numbers add a
   different table offset and are not Linux virtual IRQs. Higher DMA IRQs are
   noncontiguous; no base-plus-channel shortcut is valid for all channels.
   No IRQ is requested or enabled by this component.
4. Replace legacy MAC-pool allocation only after proving the SBG3300 pool-slot
   or supported DT/NVMEM address contract. No generated or guessed address is
   used here.
5. Obtain/reconstruct legal DSL control/PHY source and firmware integration.
   The separate stock import counts (82/31) are unaffected by this ring build.

No OpenWrt runtime, DSL sync or packet transport is claimed. Hardware remains
untouched; the module artifact stays local.
