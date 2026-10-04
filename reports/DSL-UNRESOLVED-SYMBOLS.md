# DSL/XTM binary imports and source-port dependencies

Status: `SOURCE-INCOMPLETE / FORWARD-PORT-PROBE-FAILED`. The available XTM
source was compiled against the staged OpenWrt 6.18.54 kernel headers in an
isolated temporary external-module harness. This is an initial compatibility
probe, not a complete driver port, and it does not prove that porting is
impossible.

## Stock module ABI

The rootfs modules are MIPS32 big-endian relocatables with
`2.6.30 SMP preempt mod_unload MIPS32_R1 32BIT` vermagic. Direct ELF symbol
inspection with host `readelf -Ws` found 82 unique undefined symbols in
`adsldd.ko` and 31 in `bcmxtmcfg.ko`. These are imports from the matching stock
kernel/vendor stack, not evidence that the objects will load on current
OpenWrt.

Notable `adsldd.ko` imports include:

- XTM control: `BcmXtm_GetInterfaceCfg`, `BcmXtm_SetInterfaceLinkInfo`
- board/AFE: `BpGetDslPhyAfeIds`, `kerSysGetAfeId`, external/internal AFE GPIO
  accessors
- vendor runtime: `kerSysSendtoMonitorTask`, `kerSysLedCtrl`, GPIO and dying-
  gasp registration
- old kernel APIs: `daemonize`, `kernel_thread`, `interruptible_sleep_on_timeout`,
  `init_timer_key`

Notable `bcmxtmcfg.ko` imports include `bcmxtmrt_request`, old timer/tasklet,
kernel-thread and character-device APIs, and C++ allocation entry points.

## Available XTM source dependencies

The public 4.12L.06B tree contains `bcmxtmrt.c` / bond code, but the XTM path is
coupled to Broadcom-only interfaces: `linux/blog.h`, `linux/nbuff.h`,
`bcmPktDma` XTM DMA, FAP DQM, BPM (`gbpm`), IQoS hooks, and XTM configuration
headers. The source registers legacy proc readers and uses vendor kernel APIs
such as `kerSysGetMacAddress()` and `getMemorySize()`.

The exact mirror lacks the Makefile-referenced
`adsldd$(PROFILE).o_save`, `bcmxtmcfg$(PROFILE).o_save`, and
`adsl_phy$(PROFILE).bin_save`. The running firmware does contain prebuilt
`adsldd.ko`, `bcmxtmcfg.ko`, and two PHY blobs, but those artifacts are not a
source or ABI-compatible input for a 6.18 kernel.

## Linux 6.18 compile probe

The first attempt had a test-harness include-path error because the vendor
checkout path contains spaces; it failed at `linux/blog.h` and is discarded as
non-evidence. The retry used a space-free source symlink and an isolated
external-module directory. A compatibility include shim was needed because the
vendor header expects removed `linux/autoconf.h`; after that, compilation
reached the vendor code and failed on concrete ABI mismatches:

- Broadcom NBuff expects `RecycleFuncP` and `sk_buff.recycle_flags`; the
  current kernel headers do not provide that old recycle ABI.
- Vendor packet-DMA headers expect `DmaChannelCfg`, `DmaDesc`, and `DmaRegs`
  declarations through the vendor include/configuration graph, which the
  current OpenWrt module build does not establish.
- Vendor `bcm_OS_Deps.h` includes removed `asm/system.h`.

The build logs are local at `/tmp/sbg3300-xtm-module-build-2.log` and
`/tmp/sbg3300-xtm-module-build-3.log`. No vendor source was modified, no module
was installed, and nothing was loaded on the router. See
`reports/DSL-6.18-COMPILE-PROBE.md` for exact harness scope and result.

## Port gate still open

1. Resolve NBuff/recycle and DMA API dependencies without importing the stock
   2.6.30 ABI wholesale; compile XTM incrementally and review every adaptation.
2. Recover and fingerprint a closer source package for the ADSL PHY driver and
   XTM configuration module before claiming the DSL control path can be built.
4. If source is recovered, port subsystem-by-subsystem and re-run unresolved
   import checks. Hardware DSL sync/PPPoE remains a separate runtime gate.

No stock vendor module was copied into or offered to the OpenWrt image.
