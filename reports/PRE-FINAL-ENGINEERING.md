# SBG3300 pre-final offline engineering

Scope: `OFFLINE-ONLY`, `PARTIAL-PORT`, `NOT-FLASHABLE`. All runtime results
remain `NOT-TESTED`. No router access or final firmware image build is authorized.

## Source and actual implementation

- Canonical OpenWrt `5edcc1c43cb97048b506168fbbe00538956796d6`, Linux 6.18.54,
  bmips/bcm63268. Preserved original profile checkout is
  `18c17336871e73ddfbab3198104d8c42df844146`.
- The nine OpenWrt patches apply through `git am` to a fresh pinned checkout.
  Reviewed source tree: `2ac5b16d7ba20467a099bf096de89c32d69a9324`.
  Example independently applied commit:
  `83363f3d4be12f5ccd8058b979209bf86b29f5e1` (commit dates may vary; tree is fixed).
- XTM code is `drivers/xtm/xtm_dma.[ch]`, `xtm_core.[ch]`,
  `xtm_ptm.[ch]` and `xtm_ptm_core.[ch]`. IRQ/NAPI, PTM netdev, TX BQL,
  RX refill/dispatch, real packet statistics and lifetime handling are compiled.
  Constructor requires an initialized, exclusively owned controller, actual
  DSL parameters and platform MAC. No automatic hardware attachment exists.
- Real Ethernet C changes are in the Linux delta
  `integration/schema-patches/0003-bcm6368-enetsw-managed-lifetime.patch`,
  delivered by OpenWrt patch 0009. They fix deferred/optional IRQ errors,
  platform MAC lookup, allocation errors, mapped-channel bounds, domain/clock/
  reset/runtime-PM lifetime, NAPI cleanup and netdev-before-resource teardown.
  `drivers/ethernet/enetsw_contract.h` is the same tested header installed by
  that patch. No register or physical port mapping is invented. The upstream
  generic random-MAC fallback remains; it is not SBG3300 provisioning evidence.
- OpenWrt package recipe, staging tool, kernel coverage fragment, artifact
  inspector, DTB contract checker and native/MIPS tests are real new code.
  XTM package has no autoload and supplies no PHY firmware.

## Completed compile/test stages

| Stage | Result and boundary |
|---|---|
| Preserved canonical kernel | Reused; original .config, Module.symvers, vmlinux and UTS hashes unchanged |
| Expanded upstream kernel | vmlinux/modules exit 0; ATM/br2684, B53 SPI, b43/brcmfmac, BCMA/SSB, USB EHCI/OHCI, GPIO keys and LEDs compiled |
| Independent kernel reproduction | `run-MXrHTQ` exit 0; .config identical to first expanded build; all 74 modules identical after removing debug/build-id for comparison |
| Reviewed Ethernet kernel candidate | `run-6IX2Ok` exit 0; kernel plus 75 modules inspected, including genuine enetsw module; this run precedes the final unused-variable cleanup |
| XTM component | `run-MImM7d` and `run-MRQGAg`: W=1/-Werror compiler/modpost 0, all 65 imports in matching kernel exports, exact identical bytes |
| Strict Ethernet component | `external-final-one` and `external-final-two`: W=1/-Werror compiler/modpost 0, all 85 imports in matching kernel exports, exact identical bytes |
| OpenWrt package integration | Selected `kmod-sbg3300-xtm` produced real .ko and APK; package/compile exit 0 for complete selected pre-final software configuration |
| DTB validation | Nine-patch source, DTC and round-trip, complete processed kernel schemas plus reviewed bindings: empty diagnostics in `run-9yVxBy` and `run-4ZGeku` |
| Native C policy tests | Ring/descriptor ownership, 10,000-step wrap/FIFO, error/cancel, PTM trailer/match/cell/VCID, Ethernet IRQ/defer/bounds pass |
| Sanitizers | Same C policy tests pass with Clang ASan/UBSan |
| MIPS execution | Same three policy binaries compiled static MIPS big endian/o32 and executed successfully by qemu-mips-static (`run-QlXPLR`); CPU user mode only |
| Python tests | 16 tests: four existing image-parser cases plus ELF/ABI/hash/import/loader and conservative DTB contract rejection tests |

Full compiler/modpost logs, exit files, source input hashes and generated
binaries remain outside public Git under `~/.cache/sbg3300-*`. Earlier failed
and intermediate candidates are retained. A compiled module is not hardware
functionality. Tests do not run the Linux IRQ/NAPI/DMA adapter on the router.

## Artifact facts

Exact hashes/vermagic/dependencies/import counts are in
`PRE-FINAL-ACCEPTED-ARTIFACTS.tsv`; the earlier expanded-kernel inventory is
retained in `PRE-FINAL-KERNEL-ARTIFACTS.tsv`.

- XTM ring + PTM: SHA256
  `be2beeddc3c1dcad5af9587dc0fca495b25e04767884050fbc22e9598de6470a`.
- Strict enetsw: 113,168 bytes, SHA256
  `89c26b4d872fb86a9f8839bbbe9f077ce64e5f7f99017d9258ccf1bd54e8f1b2`.
- Both: ELF32 MIPS big endian/o32, vermagic
  `6.18.54 SMP mod_unload BMIPS 32BIT`, missing kernel imports 0.
- Disabled SAR resource fixture DTB before the USB dependency correction: SHA256
  `fccf54e805a0ac96d1a0b0e6312169d334c9cfc0bdb744bf75afed5cf5615465`.
- Existing initramfs loader remains unchanged: SHA256
  `3961a39d5d554ce467b9575bbc6f6293d385ddda9fc4dc9b3dbf0c3cf8027b51`.

## Negative findings and corrections

1. Initial Kconfig dropped b43/brcmfmac because WLAN_VENDOR_BROADCOM was off.
   Dependency was enabled and both drivers actually built. A symbol request
   without a produced artifact is not counted as build success.
2. Relocated OpenWrt host pkg-config files still referred to the original
   staging directory. Duplicate endian compatibility headers broke apk host
   compilation. Relocated only sandbox metadata, preserved failed Meson state,
   reconfigured, and rebuilt successfully. A package compile before selecting
   its Kconfig symbol was a no-op; only the selected, real .ko/APK counts.
3. Full DTS validation found inherited switch/MDIO activation, incorrect
   binding names/types/compatible chains, and a pin property typo. Actual
   driver-consumed contracts were corrected; full schema checks then passed.
   SAR fixture cannot be enabled under its local schema (negative test rejects
   status=okay). No DSA topology is inferred from the generic CPU port.
4. Strict enetsw compilation exposed an unused TX variable in upstream code.
   Removed that variable while retaining skb_put_zero behavior; no warning
   suppression added. Strict fresh builds now pass.
5. Kernel patching under the OpenWrt Git subdirectory skipped some diff paths.
   Source/header comparison caught it; that integration build was interrupted
   with exit 143. Source state/logs were preserved. Helpers now use explicit
   patch -d/-p1 with dry-run and verify the installed header.
6. Strict loader audit rejects the old initramfs ELF: it has unspecified ABI
   flags and its only LOAD segment is R, without X. This does not prove CFE
   rejects it, but no CFE compatibility result exists. No image bytes changed.
7. Original NAND summary mixed legacy ECC code/OOB units with modern binding
   values. In upstream brcmnand, spare size is per 512-byte sector; Hamming can
   use code 15 when spare size is 16. The stock summary does not establish the
   modern tuple. NAND is now disabled and unverified ECC/OOB overrides removed.
8. Checkpatch retains informational MAINTAINERS warnings for added files and
   host-branch uint32_t/u64 style checks in the shared test header. No source
   compiler error is hidden. These local research patches have no fabricated
   upstream DCO sign-off.

## Defensible offline boundaries and irreducible blockers

| Subsystem | Implemented/examined offline | Exact blocker |
|---|---|---|
| XTM SAR/platform | Exact-family descriptor/channel/global register and IRQ resource facts; clock SAR 9, reset 3, domain 0; RX0 hwirq 26, TX4 hwirq 59; disabled DTS/schema fixture | Exclusive global SAR/PHY/FAP ownership, initialization/reset sequence and real DSL-configured match/VCID/trailer state unavailable; no active platform probe |
| Legacy probe | Separate canonical object/module inventory preserved | Still 19 imports (15 PacketDMA, 3 legacy IRQ, 1 MAC allocator); not relinked. New module is a separate implementation, not dummy legacy exports |
| DSL | PTM transport policy/frontend and real link-event API; upstream ATM/br2684 and firmware loader compiled | Inspected exact-family mirror has bcmxtmcfg header but no adsldd/bcmxtmcfg implementations; no legally approved PHY blob/container/load/boot/mailbox contract. No source-backed PHY/control producer, ATM cell attachment or DSL sync |
| Ethernet/BCM53125 | Real enetsw resource fixes, B53/MDIO/HSSPI/DSA/VLAN code compiled; exact-board source reviewed | 2015 board entry has C2/C3 variants and conflicting CS-overlay/HS-SPI group evidence. Actual switch ID, CPU interface/delays, jack map, PHY/reset wiring and board MAC provisioning remain unproved; switch/MDIO/Ethernet disabled |
| Wi-Fi | b43/brcmfmac, BCMA/SSB compiled; pin's ID tables inspected | 14e4:435f band case is not a PCI bind entry. No verified host glue/SPROM/calibration/firmware/regulatory contract; no guessed ID patch or calibration |
| Peripherals | USB HCDs and PHY, GPIO/pinctrl, LED drivers, GPIO input, watchdog and clocks/resets compiled | Board electrical/polarity and runtime behavior untested; no guessed LED/button map enabled |
| NAND/boot/image | brcmnand compiled, historical partition arithmetic/container tests retained, conservative DTS and loader audit | Modern ECC/OOB tuple, exact Zyxel writer/bad-block translation, complete physical layout, CFE loader acceptance and non-UART recovery unproved. No fixed partitions/factory/sysupgrade image |

The source search included both local mirrors; missing Hermes private research
is not the sole blocker. Mirrors are unchanged and excluded from publication.
The inspected family revision is `e2f23ddbb20bf75689372b6e6a5a0dc613f6e313`;
later comparison `1555117dd9e5b393cf5b92e10e603e1c5f8ba2bb` is not an ABI substitute.
The stock inventories adsldd (82) and bcmxtmcfg (31) stay separate from XTM (19).

Zyxel's official source-request channel is available at
https://www.zyxel.com/global/en/form/gpl-oss-software-notice. No request or
message was submitted. Search did not deliver exact lawful DSL implementations;
it does not prove no source exists elsewhere.

Before a final Full OpenWrt image is technically justified: obtain lawful
control/PHY material and actual interface contracts, establish controller
ownership and board topology/calibration/storage/boot evidence, then integrate
and validate those implementations. Every device diagnostic/runtime/boot test
needs separate explicit authorization. No UART, raw MTD/NAND, device module
loading, configuration change, reset/reboot or flash is part of this work.

USB dependency review additionally found that the old skeleton enabled EHCI/OHCI
but left their upstream exact-SoC PHY disabled. Patch 0005 enables that existing
provider; a new rejection test enforces this dependency. No VBUS GPIO or board
calibration value is guessed. This changes the fixture DTB hash; final validation
records are appended after the new source-tree check.

## Final integrated software results

- Source sandbox OpenWrt HEAD `9d363a34768ce05e7d229242408b3fdf77b29651` has exactly the reviewed tree
  `2ac5b16d7ba20467a099bf096de89c32d69a9324`. Prepared kernel source was patched
  explicitly and its enetsw source/header compared byte-for-byte to the strict
  module inputs before the successful integration build.
- Corrected integrated vmlinux/modules build exits 0. Integrated vmlinux SHA256:
  `bdb6d92f68fd401655b1d2c9ba7901719833dec1b423273b913c13911c0c27ee`.
  The prepared-tree build is separate from a final firmware image build.
- Selected complete package/compile exits 0; 88 APK files present in the sandbox.
  Original signing keys and generated package files remain private.
- Final source DTB/full-schema/round-trip and dependency test pass in
  `~/.cache/sbg3300-offline-dts/run-ke2Pf5`, with empty diagnostics. DTB SHA256:
  `3be99ff1c7e4962384cd292adfd408cace5439625c381026619f60946a99751d`.
- No final production/factory/sysupgrade/rootfs image target was started. Existing
  initramfs ELF and canonical kernel inputs retain their original hashes.
- Raw Git whitespace diagnostics are normal unified/nested patch context, not
  applied source defects; both checker results are retained. Scanner contact
  findings are reviewed published upstream author attribution, retained intact.

## Gate assessment

All available independent safe offline implementation/build/test stages above
have been performed. Source, hardware and firmware blockers in the table remain.
A final Full OpenWrt image is **not technically justified** at this boundary.
The decision is BLOCKED, not COMPLETE. Obtain new lawful source and exact
controller/board/storage/boot evidence before extending runtime attachment or
considering the separately approved final build. Device authorization remains
separate from source/build approval.
