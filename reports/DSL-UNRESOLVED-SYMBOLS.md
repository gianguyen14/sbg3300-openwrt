# DSL/XTM binary imports and source-port dependencies

Status: `BUILD-NOT-ATTEMPTED`. The OpenWrt target toolchain/kernel headers are
not ready yet. This report records binary ABI evidence and source dependencies;
it does not claim that a modern-kernel forward port is impossible.

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

## Port gate still open

1. Complete current upstream bmips baseline and stage 6.18 headers/toolchain.
2. Configure the isolated SBG3300 kernel profile; compile the available XTM
   implementation only, recording every missing Broadcom API and kernel API.
3. Recover and fingerprint a closer source package for the ADSL PHY driver and
   XTM configuration module before claiming the DSL control path can be built.
4. If source is recovered, port subsystem-by-subsystem and re-run unresolved
   import checks. Hardware DSL sync/PPPoE remains a separate runtime gate.

No stock vendor module was copied into or offered to the OpenWrt image.
