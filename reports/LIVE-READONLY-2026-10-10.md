# Authorized stock SSH diagnostics and offline TX correction

Date: 2026-10-10. Evidence: `LIVE-DEVICE` / `STOCK-BOOT-LOG`, collected
through the owner's existing SSH setup. Source parent:
`b89c4408c1edfd4d7545f099e25dbfc19aca82b2`.
Overall remains `PARTIAL-PORT`, `OFFLINE-ONLY`, `NOT-FLASHABLE`.
Runtime correction/test/evidence commit:
`c034751f24e150a97206fab03f266367b142526f`.

## Connection, collection and privacy

`type -a sbg3300` identified an existing executable using Expect and SSH.
Its existing authentication and legacy algorithms were reused. A private copy
changed `StrictHostKeyChecking=accept-new` to `yes`; the saved host key verified
and authentication succeeded. Original SSH configuration/executable unchanged.
No credentials, destination, host keys or authentication values are published.

Raw output is outside Git in `$HOME/.cache/sbg3300-readonly-20261010/`, with
directory mode 0700 and logs mode 0600. Only manually selected hardware facts
are in this report. No MACs, bridge identifiers, network addresses, serials, calibration,
NVRAM contents, firmware contents or persistent settings were added to Git.

Collected uname, CPU/cmdline/IRQ/iomem/MTD/partition/module metadata, ifconfig,
network counters, bridge membership, dmesg, PCI/SPI/platform/net/USB sysfs
metadata, directory listings and confirmed `xdslctl info --show` status.
The XTM RX/TX proc info readers were inspected in the family source before
reading them: `bcmxtmrt.c:4827` / `:4956`, revision below; no control writes.
The four-value `/proc/brcm/kernel_config` summary is not a full kernel config.

One long sysfs batch was truncated by the stock command path before its end
marker. It is retained as a partial result; short subsequent batches completed
the peripheral/path observations. `readlink`, ethtool and lspci were unavailable;
symlink listings and proc PCI metadata supplied binding evidence. Missing
sysfs attributes are unavailable evidence, never guessed values.

No firmware modification, module loading, interface change, reset/reboot,
UART, raw flash read/write or register/control write occurred. No final
firmware/image build started.

## Subsystem observations and exact limits

| Subsystem | Direct stock observation | Effect on the port |
|---|---|---|
| CPU/SoC | Board `963168MXH_17A`, two Broadcom4350 V8.0 CPUs; boot log chip `0x631680D0` and BCM63168D0 Ethernet driver; Linux 2.6.30 | Corroborates exact-family selection; does not establish Linux 6.18 runtime |
| Driver ownership | Loaded `bcm_enet`, `adsldd`, `bcmxtmcfg`, `bcmfap`, `bcm_bpm`, `bcm_ingqos`, proprietary `wl`; XTM proc entries exist | XTM is not a separately listed `bcmxtmrt` module here; module absence does not mean runtime absence |
| XTM/FAP | Boot reports FAP PacketDMA binding, FAP1 PSM allocations, RX channel 0 with 200 BDs and channel 1 with 16; PTM/ATM non-bonding mode | Current stock descriptors are not evidence of independent host ownership; do not adopt their addresses or reset SAR/FAP |
| XTM snapshot | RX0/RX1 report cfg/status 0, interrupt mask 7, assigned BDs 0; TX info empty while DSL idle | Snapshot only; neither proves DMA teardown nor authorizes ownership transfer |
| IRQ | Stock WLAN IRQ 15, OHCI 17, EHCI 18, DSL 31, anonymous brcm entries 32/33; no separately named SAR DMA handler | Stock logical IRQ numbers must not be copied into DT interrupt specifiers; source SAR mapping remains source evidence |
| Ethernet | `bcm_enet`; boot maps eth0 to stock switch port 4, eth2 to 2, eth3 to 1, eth4 to 11 and eth5 to 12; snapshot eth0/eth2/eth4 carrier up | These are stock logical indices, not physical jack or DSA CPU-port proof. Bridge/VLAN/PPP devices exist; DSL is idle, so PPP presence is not DSL-sync proof |
| SPI/switch | `bcmhs_spi.1`, `spi1.0` modalias/driver `bcm_HSSpiDev0`; legacy SPI controller also present | Resolves observed SPI instance/stock binding. No switch silicon ID, upstream chip-select equivalence, CPU port, RGMII delay or jack mapping proven |
| Wi-Fi | PCI `14e4:435f`, subsystem `14e4:0513`, class `0x028000`, bound `wl`, IRQ 15; wl0 maps to that PCI function | Confirms stock PCI binding, not BCMA/SSB/b43/brcmfmac compatibility |
| Wi-Fi calibration path | Boot explicitly reports SROM/OTP not programmed, memory-mapped SROM information and loading `/etc/wlan/bcm6362_map.bin` plus common NVRAM-variable file | Stock uses an external calibration/data path. Files were not read or redistributed. Format, provenance and lawful upstream calibration provision remain unresolved |
| DSL | `xdslctl info --show`: Idle, retrain reason 0, last initialization procedure status 3, link power state L0 | No synchronization at observation. No initialization/retrain/control command sent; PHY source/firmware integration remains blocked |
| USB | PCI `14e4:6300` functions bound OHCI/EHCI, classes `0x0c0310`/`0x0c0320`; root hubs `1d6b:0001`/`0002` only | Confirms stock HCD discovery, not OpenWrt VBUS/peripheral operation |
| NAND | `brcmnand.0` driver; iomem `0x10000200..0x10000383`; MTD rootfs `0x016a0000`, data `0x00400000`, nvram `0x00020000`; each erase 131072/page 2048/OOB 64 bytes | Geometry corroborated without raw reads. `ecc_strength` and `ecc_step_size` missing; total physical layout, ECC mode/OOB-per-sector, writer/BBT/slot/CFE compatibility still unproven |
| GPIO/LED/button/watchdog | No corresponding standard sysfs classes in this stock kernel | Cannot establish wiring, polarity or absence of hardware. No vendor control utility used |
| Clock/reset | No standard clock/reset ownership metadata exposed by inspected stock interfaces | SAR/DSL sequencing and ownership remain unresolved |

Family source consulted privately, unchanged:
`nomis/bcm963xx_4.12L.06B_consumer` revision
`e2f23ddbb20bf75689372b6e6a5a0dc613f6e313`. Its
`shared/opensource/include/bcm963xx/63268_intr.h` uses logical offset 8:
stock DSL 31 corresponds to hardware input 23, USB 17/18 to 9/10 and WLAN
15 to 7. This corroborates numbering conventions. It does **not** establish
stock SAR IRQ registration: RX0 input 26 would be logical 34; TX hardware
channel 4 input 59 would be logical 67. Those handlers were not observed.
The disabled SAR fixture remains inputs 26/59, never logical 34/67.

The stock `/proc/switch` and `/proc/mii` interfaces are register-selection
interfaces in this family source, not automatic identification endpoints.
They were only listed. No selector writes or guessed switch utility calls
were made. Further switch identification needs an independently established
safe status interface or separately approved experiment.

## Actual changed runtime code and tests

`drivers/xtm/xtm_ptm.c`: acquire TX lock and check link/ring admission **before**
linearizing or padding the skb. `NETDEV_TX_BUSY` now retains the unchanged
packet for the network stack. Keep admission/preparation/submission serialized;
failure paths unlock and consume once. No hardware binding added.

`tests/test_xtm_xmit.c` and `tools/extract-xtm-xmit-test.py` execute the actual
callback body with CPU-only kernel API doubles. Eight cases cover full queue,
link down, excessive length, linearization failure, padding failure, submission
failure, successful padded submission and final-slot backpressure. Assert lock
balance, skb retention/free/consume, drop stats and BQL bytes. Doubles exist only
in tests; they are not runtime shims or dummy kernel exports.

The same regression test aborts on the pre-fix callback (exit -6, assertion
that BUSY leaves length 42 unchanged). That failure and source are retained
privately under `tests/negative-before-fix/`. New tests pass natively, with
Clang ASan/UBSan, and as static MIPS BE/o32 executables under user-mode QEMU.
Existing descriptor/PTM/Ethernet tests and 16 Python tests pass. Shell syntax,
Python compilation and the incremental whitespace check pass.
The subsequent coverage-checker tests add three Python cases, for **19 total**.

## Genuine build results

Pinned OpenWrt `5edcc1c43cb97048b506168fbbe00538956796d6`, preserved profile
checkout `18c17336871e73ddfbab3198104d8c42df844146`, Linux 6.18.54.
Two independent fresh external builds reuse the preserved kernel, W=1,
KCFLAGS=-Werror: compiler/modpost exit 0, identical full module bytes.

| Artifact | Bytes | SHA256 |
|---|---:|---|
| Fresh external `sbg3300_xtm_dma.ko` | 130820 | `f67b6da34dcc279ee832fbc4210463b8cc89ba2b184186309d324e70e47f80dd` |
| Updated isolated OpenWrt package-build module | 134840 | `31ae19d6a322e85679095e469379598988bd8af37b68a505383a75c8933adfbf` |
| Updated `kmod-sbg3300-xtm-6.18.54-r1.apk` | 9638 | `11dae7f9a8cad685cc05a8961312daaf4a9fbc4e0795ed04f51782306fb3239d` |

Both modules: ELF32 MIPS big-endian/o32; vermagic
`6.18.54 SMP mod_unload BMIPS 32BIT`; 65 kernel imports, none missing,
no external module dependencies. Package compile exit 0 with actual CC,
MODPOST and LD, source byte comparison passed. Different build paths/debug
context explain distinct external/package artifacts; not claimed identical.
These hashes supersede the previous XTM component/APK for this callback change;
the historical PRE-FINAL artifact/package TSVs retain their previous build
snapshots. The other validated kernel, Ethernet and package results are unchanged.

Private complete logs: external runs `run-YuhQUT`, `run-JAMWl6` under
`$HOME/.cache/sbg3300-xtm-runtime/`; package `xtm-package-compile.log` and
ELF audits in the read-only evidence directory; MIPS tests `run-7osc4w`.
Original kernel/image and earlier modules/APK preserved; previous package
build copied under `package-before-tx-fix/` before rebuilding.

The legacy probe still has **19 unresolved imports**. Stock `adsldd` 82 and
`bcmxtmcfg` 31 inventories remain separate. These new module builds do not
relink the legacy probe or prove SAR initialization, DMA/IRQ operation,
netdev traffic, DSL synchronization, radio or boot.

## Additional BCMA SoC-host compile boundary

Family source supplies a software PCI header for the on-chip WLAN with the
observed slot/ID/subsystem. It is not proof of a discrete PCIe radio. See
WIFI-UPSTREAM-REVIEW.md for exact source paths and the source/live mapping
discrepancy. The pinned prepared kernel's fallback-SPROM implementation rejects
SoC hosts; adding a PCI ID does not resolve bus or calibration integration.

`configs/kernel-pre-final.fragment` now covers CONFIG_BCMA_HOST_SOC=y only in
the isolated compile environment; BCMA serial flash explicitly disabled.
No SBG3300 BCMA node or calibration provider added. The helper now validates
negative Kconfig selections as well as positive ones. Three tests run its actual
shell loop: valid selections pass, dropped host and enabled serial-flash fail.
A first private fixture invocation lacked rg in its artificial PATH; its failure
was retained, then the fixture used the existing PATH and all cases passed.

Build root: `bcma-soc-kernel/run-BmtL8Z` inside the private evidence directory.
The initial helper invocation ended **127**, reporting `vmlinux: command not
found`, after artifacts had been produced. The helper was edited while its Bash
process was still executing; the subsequent erroneous command overwrote that
target's compiler log. The original complete kernel compiler log is therefore
**not available**, and this invocation is not labelled a clean build success.
The failure/log is retained. A stable explicit `vmlinux modules V=1` repeat
exits **0** with .config/Module.symvers/vmlinux/UTS hashes unchanged. Its log is
`corrected-compiler-modpost.log`. No original build tree was changed.

Audit: **77 kernel modules**, all ELF32 MIPS BE/o32, expected vermagic, no
unresolved imports against the real Module.symvers. Inherited FSL USB modules
are compile coverage, not SBG3300 USB hardware support. Two fresh independent
external BCMA builds include real host_soc.c, using -Werror (not W=1), each
compiler/modpost exit 0, zero warnings, identical complete module bytes.
Both full C/compiler/modpost logs are retained as `external-one-compiler-modpost.log`
and `external-two-compiler-modpost.log`; 73 real imports, none missing.

| Artifact | Bytes | SHA256 |
|---|---:|---|
| SoC-host coverage vmlinux | 58793900 | `41c3452a3b18130026a62f4a242db4c152e79580cf2375d139d4007fb6ee1a64` |
| In-tree BCMA PCI + SoC-host module | 316020 | `213112dcbb73010ca8fb638a66e04867ae55d6c3b0d33a3abb28c67c8da37362` |
| Reproduced external BCMA module | 315528 | `58a464ca7d1eb9094df33df332291ad2bc9a378d52b5d8dff1abf541d3baefd0` |

Configuration SHA256:
`955b90720b5ace2ac4e2cd05f95486b33686b14966f178757b3649188f9f7569`.
Verbatim module hashes/dependencies are in LIVE-READONLY-KERNEL-ARTIFACTS.tsv.
Kernel repeat stability and external-module reproduction do not constitute an
independent clean reproduction of this entire new kernel configuration. Earlier
independent kernel results are retained for their previous configuration.

## Publication and gate

Final source-consistency review found that the standalone `dts/` board file
still held the old enabled NAND/ECC overrides, although the nine-patch OpenWrt
board and compiled SAR fixture were already conservative. It now exactly
matches that reviewed OpenWrt board: NAND/switch/MDIO disabled, ECC/OOB overrides
removed, existing USB host PHY provider enabled consistently. No new topology.
The DTS validation helper compares both board sources before compiling; the
old standalone source negative fixture is rejected with exit 1 before build.
Full DTC/roundtrip/meta-schema/board-schema/disabled-resource checks pass with
zero diagnostics in `$HOME/.cache/sbg3300-offline-dts/run-Lnzl8o`.
DTB SHA256 remains
`3be99ff1c7e4962384cd292adfd408cace5439625c381026619f60946a99751d`.
Board source retains its GPL-2.0-or-later license; helper addition is original.

Changed runtime/test/tools are original GPL-2.0-only source; no vendor bodies,
stock binaries, private logs or firmware included. Existing upstream copyright
and contact attribution retained. Local scanner findings remain those reviewed
upstream contacts; scanner rules unchanged. The full inherited patch-series
whitespace findings remain recorded in PRE-FINAL-PUBLICATION-REVIEW.md; do not
confuse incremental clean diff with a clean origin/main triple-dot check.

File-level review: runtime callback and extracted-body test/harness contain
only original source; test runners contain local compile/emulation commands;
STATUS/HANDOFF/start/read-only guidance and YAML contain reviewed facts and
scope updates; this report contains selected non-identifying hardware evidence
and offline build results. Coverage fragment/helper/three tests are original;
Wi-Fi follow-up is attributed source facts, not copied vendor implementation;
artifact TSV contains only audited software metadata. All approved for publication, no additional vendor
licensing claim. Staged scanner: 118 tracked files, 410 reachable objects,
raw exit 1 for two legitimate upstream contacts and their history occurrences.
Incremental `git diff --cached --check` exit 0; `git diff --check
origin/main...HEAD` raw exit 2 with the same 271 patch-format diagnostics.
Neither scanner nor whitespace settings were weakened. Logs retained privately.
An extra EOF blank line introduced in the publication-review follow-up was
reported by the next incremental whitespace check and corrected before push.

Read-only evidence narrows discovery/stock ownership/calibration questions but
does not resolve lawful DSL PHY/control implementation, exclusive SAR/FAP
transition, external switch topology, upstream Wi-Fi bus/calibration, NAND
ECC/writer/CFE acceptance, or a non-UART recovery path. No additional hardware
activation is defensible from this observation. Existing independent kernel,
Ethernet, packages and full DTS validation remain valid; the additional kernel
coverage build above preserves those earlier artifacts. No final
production/factory/sysupgrade image is justified.

Further device-state experiments, OpenWrt/module execution, interface/link
changes and recovery/boot testing require separate specific owner approval.
No UART or raw flash operation is proposed.

**PRE-FINAL-BUILD BLOCKED — AWAITING USER DECISION**
