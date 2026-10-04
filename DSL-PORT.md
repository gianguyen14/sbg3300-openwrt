# BCM63168 DSL/XTM port investigation

## Stock runtime evidence

The live stock kernel is 2.6.30. It loads proprietary modules including
`adsldd`, `bcmxtmcfg`, `bcm_enet`, `bcmfap`, `bcm_bpm`, and `bcm_ingqos`.
Boot messages identify BCM63168D0 ADSL/XTM, XTM ATM/PTM non-bonding, and the
network path `ppp2.1 -> eth4.1 -> eth4`. Exact ISP configuration values are not
included here.

The extracted stock rootfs has two ADSL PHY files (`adsl_phy.bin` and
`adsl_phy1.bin`) and the above kernel modules. These files are proprietary
firmware artifacts; hashes and metadata may be recorded locally, but they are
not to be redistributed without license review.

## Public source candidate located

The extracted stock DSL-related modules are ELF 32-bit MSB MIPS relocatable
modules. Their vermagic is `2.6.30 SMP preempt mod_unload MIPS32_R1 32BIT`;
per-module hashes and dependencies are in `reports/STOCK-MODULE-INVENTORY.txt`.
This is an ABI fingerprint only. These binary modules are not compatible
artifacts for a Linux 6.18 kernel.

The OpenWrt BCM63xx hardware reference identifies the `100AAPP7D0_4.12L.06B`
BCM63168D0 Linux 2.6.30 source family. A public Git mirror was located at
`nomis/bcm963xx_4.12L.06B_consumer`, commit
`e2f23ddbb20bf75689372b6e6a5a0dc613f6e313`. It contains the exact
`963168MXH_17A` board-parameter entry and `bcmxtmrt` source, making it a strong
lineage match rather than a generic SoC sample. It is a 2015 mirror, while the
running kernel is a 2018 build; module/source equivalence is not yet proven.
The OpenWrt reference page identifies this release family and links the exact
archive at
`https://osdn.net/projects/zyxel-vmg3312/downloads/68893/100AAPP7D0_4.12L.06B_consumer_release.tar.gz/`.
Direct
retrieval was retried on 2026-10-04 but the workstation could not resolve
`osdn.net`; the inspected Git mirror is therefore not claimed to be identical
to the linked archive. A second 3.4 source lead (`100AAJX8_4.16L.02A`) is linked
from Google Drive and is explicitly described there as including closed code;
it remains a separate un-retrieved lead.

In the source tree, `bcmdrivers/opensource/net/xtmrt/impl4` has C sources, but
`bcmdrivers/broadcom/char/adsl/impl1` and `char/xtmcfg/impl2` contain Makefiles
without their implementation sources. The stock rootfs contains `adsldd.ko`,
`bcmxtmcfg.ko`, and PHY firmware. Thus XTM data-path source is available, but
the critical DSL PHY and XTM configuration implementations appear to be
closed/prebuilt in this source mirror. Continue checking other public releases
and exact module fingerprints before classifying the port as blocked.

The source Makefiles refer to excluded `adsldd$(PROFILE).o_save`,
`bcmxtmcfg$(PROFILE).o_save`, and `adsl_phy$(PROFILE).bin_save` files. Those
objects/blobs are absent from this mirror. It exposes public ADSL/XTM headers
and the XTM network driver implementation, but the PHY driver and config module
are not rebuildable from the checked-in tree. The OpenWrt BCM63xx technical
reference independently identifies the 4.12L.06B BCM63168D0 source family and
describes the DSL support gap. That community status page is corroborating
context, not proof that no matching source exists elsewhere. The specific
missing source objects in the inspected mirror remain the stronger evidence.

Reference: https://openwrt.org/docs/techref/hardware/soc/soc.broadcom.bcm63xx

A second public Broadcom driver repository, `jclehner/bcmdrivers-gpl-bcm963xx`
(pinned locally at `1555117dd9e5b393cf5b92e10e603e1c5f8ba2bb`), was also checked.
It has a larger, later XTM implementation (`impl5`) with DMA/BPM/runner split
files, but no `char/adsl` or `char/xtmcfg` source directory and no saved driver
objects or PHY blob. Its tree contains later chip families (for example 963138
and 96858) and is not established as BCM63168 source. It therefore expands the
XTM comparison material but does not supply the missing SBG3300 PHY/config
driver or a valid forward-port source baseline.

The available `bcmxtmrt.c` source is not a self-contained network driver. It
includes Broadcom-only `linux/blog.h`, `linux/nbuff.h`, `bcmPktDma.h`, and
XTM configuration headers, and calls vendor `getMemorySize()` and
`kerSysGetMacAddress()` interfaces. It also registers legacy `/proc` readers
with `create_proc_read_entry()`. Those are identifiable porting tasks against
the current kernel, but solving them would still not supply the missing
`adsldd` PHY implementation or `bcmxtmcfg` configuration/control plane.

Further release search found two more source leads: Sky's SR102 repository
points to `SKY-IHR-2-1-s-3761-R-consumer-release.tar.gz`, and Actiontec's
official T1200 GPL page lists `bcm963xx_gpl_t07_consumer_release` for 31.128L.07
and 31.128L.08. Their web pages and likely archive hosts timed out from the
workstation in this pass, so these archives were not recovered or fingerprinted.
The SR102 GitHub project itself includes CFE/NVRAM/JTAG and firmware artifacts;
it was treated only as a pointer to the Sky-hosted source URL, not used as a
driver source or release artifact. These unretrieved vendor-source leads keep
the DSL source search open.

## Forward-port strategy

The stock ADSL/config module imports were also enumerated directly from the
extracted ELF files: `adsldd.ko` has 82 unique undefined symbols and
`bcmxtmcfg.ko` has 31. Key dependencies and the still-open compile gate are
listed in `reports/DSL-UNRESOLVED-SYMBOLS.md`. An OpenWrt 6.18 compile attempt
has not yet been made because the pinned upstream baseline toolchain is still
building.

1. Inventory every stock `.ko`: architecture, vermagic, imports/exports, strings,
   dependencies, and userspace ioctl/config clients.
2. Search for official Zyxel GPL sources and Broadcom BCM63168 release sources.
3. Match any candidate source to exact stock module fingerprints before porting.
4. Port one subsystem at a time to the current bmips kernel; never load 2.6.30
   vendor modules into a modern kernel.
5. Build an OpenWrt package/procd/netifd integration only after kernel API and
   XTM interface are understood.

Compile success will not be reported as DSL support; DSL sync, line parameters,
XTM data path, and PPPoE need hardware runtime evidence in a future authorized
stage.
