# Offline boot, storage and peripheral validation

Pinned OpenWrt `5edcc1c43cb97048b506168fbbe00538956796d6`, Linux 6.18.54;
review performed 2026-10-10 UTC / 2026-10-11 local time. `OFFLINE-ONLY`,
`NOT-FLASHABLE`. DSL remains deferred.

## Actual validator corrections

`tools/sbg3300-image-info` previously accepted any board ID beginning with
`963168MXH_17A`, including a different ID with an appended suffix. It now
requires the exact ID. Unknown trailer flag values are rejected. Tests use
otherwise valid synthetic containers with recomputed CRCs, so identity/format
rejection is independent of CRC mismatch. This does not emulate stock image
acceptance or authorize use of the container on NAND.

`tools/audit-kernel-artifacts.py` now rejects negative string offsets, physical
LOAD range overflow, invalid ELF alignment/congruence, overlapping loader
virtual/physical ranges, and entry points in zero-filled rather than file-backed
code. Existing explicit ABI, architecture, executable-segment and module import
checks remain. New negative ELF fixtures cover each failure.

`tools/check-offline-dtb.py` now rejects enabled/default-enabled BCMA SoC hosts,
GPIO LED and button consumers whose board wiring/provisioning is unverified.
Disabled research nodes remain permitted. No board DTS node was activated.
Full DTC/round-trip/binding meta-schema/full DT schemas and both disabled
fixtures pass with empty diagnostics in `sbg3300-offline-dts/run-V8bJmB`.
The board/candidate DTB hashes remain `3be99ff1c7e4962384cd292adfd408cace5439625c381026619f60946a99751d`
and `d3e7522c76ace2a0fb567c3f0fc6178b45648b171db655d4f9faa7f74f10ec91`.
Python unit suite: 29 tests pass. These are original offline tool/test changes;
no firmware, private hardware data or vendor implementation is included.

## Existing loader and CFE boundary

The preserved initramfs ELF remains SHA256
`3961a39d5d554ce467b9575bbc6f6293d385ddda9fc4dc9b3dbf0c3cf8027b51`.
It has entry `0x81000000`, ABI flags 0, and one R-only LOAD segment at that
address, file/memory size `0x5966ff`. Strict loader audit still fails, exit 1:
entry outside executable LOAD segments. No artifact bytes were changed.

`UPSTREAM`: pinned `target/linux/bmips/image/lzma-loader/src/Makefile` converts
the linked loader to a raw binary, wraps that binary with ld's binary input,
then links it using `loader2.lds`. That script collects binary `.data` into
`.text`; this explains the outer ELF's loss of original ABI/execute metadata.
It does not establish how this board's CFE accepts ELF program headers.
`loader.c:126–168` forwards four boot arguments to the decompressed kernel.
Linux `arch/mips/bmips/setup.c:484–490` accepts an explicit DTB boot convention
or searches its built/appended DTB. CFE handoff, RAM reservations, loader
relocation/workspace overlap and cache semantics remain exact-board blockers.
The public same-board-ID log shows a stock load/entry pair `0x80020000` /
`0x8035c2e0`; this is a stock kernel example, not mandatory addresses for a
replacement kernel. No final image or RAM boot was attempted.

The [Zyxel-hosted recovery discussion](https://community.zyxel.com/en/discussion/6296/sbg3300-n-bricked-how-to-recover-back)
uses a console to enter CFE before its web recovery. That procedure does not
provide an approved non-UART entry method here. The public bootlog's host-run
option is a lead, not a verified owner-accessible RAM-only command. Exact CFE
source or authenticated non-console recovery instructions are needed before
proposing any device boot experiment.

## NAND translation finding

Public mirror revision `e2f23ddbb20bf75689372b6e6a5a0dc613f6e313`, independently
checked byte-for-byte against the pinned public source for the reviewed NAND
file. `kernel/linux/include/linux/mtd/brcmnand.h:558,580` encodes Hamming as 15
and three ECC bytes. `brcmnand_base.c:10747–10749` selects Hamming's
`brcmnand_oob_64`, despite printing an erroneous BCH4/4K layout label. Thus that
printed label alone is not proof of BCH4 or a 4-KiB page. The same-board-ID log
reports 2-KiB pages, 64-byte OOB, four 512-byte steps and three ECC bytes/step.
Linux 6.18 `brcmnand.c:1134–1135` translates code 15 with 16-byte spare/sector
into strength 1. This is `SUPPORTED` interpretation; actual device ECC settings/BBT compatibility and equivalence to the owner's
writer are not established.
NAND, fixed partitions and firmware image generation remain disabled.

## USB, GPIO, pinctrl and watchdog

`UPSTREAM`: `phy-bcm63xx-usbh.c` has the BCM63268 variant, clock/reset/PM
resources and native-CPU-endian setup. EHCI/OHCI use its existing provider,
with big-endian bindings in the reviewed SoC DTS. No board VBUS GPIO is added.
`pinctrl-bcm63xx.c:41` matches `brcm,bcm63268-gpio`; generic gpio-mmio alone is
not the board's full GPIO binding. Gate/timer clocks, reset, power domains and
BCM7038 watchdog have compiled objects. Eight actual object hashes/ABI facts
are recorded in `NONDSL-PERIPHERAL-OBJECTS.tsv`; no Kconfig-only success is
counted. LED/key/HCD modules remain in the full kernel artifact ledger.

Exact boardparms source encodes boot power/stop GPIOs 20/21 active-low, several
serial LED channels, and external interrupt 0/1 button roles. These are source
encoding facts, not confirmed electrical wiring, and no consumers are enabled.
Required board evidence remains LED routing/mux/polarity, button signal/polarity,
USB power/overcurrent wiring and actual OpenWrt runtime operation.

## Integrated kernel results

A private reflink copy of the verified BCMA SoC coverage kernel received the
exact new enetsw C/header. Actual vmlinux/modules V=1 build exits 0 with zero
compiler/modpost warnings/errors. Source configuration SHA256 remains
`955b90720b5ace2ac4e2cd05f95486b33686b14966f178757b3649188f9f7569`.
Original kernel .config/symvers/vmlinux/UTS hash checks pass unchanged.

New vmlinux: 58,793,952 bytes; SHA256
`ddfcb7681c002a505eb5ebcd553c61c5c666b9b4d8b36a02f6a4c64be745b8fc`.
All 77 modules pass actual ELF32 MIPS BE/o32, vermagic and real-export audits;
missing imports 0. Full hashes are in `NONDSL-INTEGRATED-ARTIFACTS.tsv`.
Integrated enetsw SHA256 `5f35916b54a81bf1a66333d6975cfce6217f0d7d437ee7f9575fe891e9bd9b09`
is configuration/path-specific, separate from the strict two-build reproduced
artifact `091acf5f6c90fc6f2bebe202343fc295817a4a95b93795e1562efafa396da7d0`.
No claim of an independently reproduced whole new kernel is made. Existing
XTM native and four-group MIPS regression suites pass without DSL development.

The remaining gate requires board-specific topology/tag transport and MAC
provisioning, lawful radio calibration/host integration, NAND writer/BBT/OOB
compatibility, CFE handoff and a safe non-UART recovery route. Compilation and
these stricter offline checks do not satisfy those runtime/hardware contracts.

## Executed boot and OOB fixtures

`tools/test-boot-elf.sh` compiles an original four-instruction MIPS userspace
exit program with the real cross toolchain. Its explicit-o32 ELF passes audit
and executes in QEMU, exit 0. Binary rewrapping through the pinned-style
pipeline loses ABI/X metadata and is rejected by strict loader audit, exit 1.
The fixture has no kernel payload, firmware, UART or device code; only the
ordinary userspace executable was run. SHA256: positive
`daea81e1ac9cffc8e1adcf4e56acffe3f36b6b9983fc7c9f3aea03ab4a3bb07d`,
wrapped negative `cde471fa47555574873aa01c0806052ef3d2c2ce5c4ba55e17fc5fde8bbb0f59`.
Logs: `sbg3300-boot-elf-tests/run-qivYON`. The synthetic reproduction explains
the strict failure without changing its criteria or proving CFE acceptance.

The pinned public `kernel/linux/include/mtd/brcmnand_oob.h:46–66` stores ECC
bytes at 6–8, 22–24, 38–40 and 54–56; free ranges are (2,4), (9,13), (25,13),
(41,13), (57,7). Actual Linux 6.18 Hamming OOB callbacks produce the same
layout for 2048-byte pages, 16 spare bytes/512-byte sector: 12 ECC bytes, 50
free bytes, and two reserved bad-block-marker bytes.
`tools/test-brcmnand-oob.sh` executes both actual extracted kernel callbacks
against these independently sourced expected regions. Native, Clang
ASan/UBSan and MIPS big-endian QEMU tests pass, including section bounds and
complete no-overlap byte coverage. This establishes conditional source-layout
equivalence for that tuple; actual media/BBT/image writer remain untested.
NAND stays disabled. The complete pinned mirror has no CFE ELF loader source.
