# XTM dependency review after local handoff

Review date: 2026-10-10. This is an offline source-map review, not a driver
implementation or runtime result. It adds no external source code to Git.

## Evidence and source boundaries

- Canonical build target: OpenWrt `5edcc1c43cb97048b506168fbbe00538956796d6`,
  `bmips/bcm63268`, Linux 6.18.54.
- The handoff's canonical external-module probe is diagnostic, uses probe-only
  compatibility code, and fails modpost. There is no XTM module artifact.
- The 19 unresolved names in
  `XTM-UNRESOLVED-CANONICAL-6.18.54.tsv` are module-object imports. This count
  is separate from the stock `adsldd.ko` inventory (82) and `bcmxtmcfg.ko`
  inventory (31) recorded in `DSL-UNRESOLVED-SYMBOLS.md`.
- Local-only source comparisons used mirror commits
  `e2f23ddbb20bf75689372b6e6a5a0dc613f6e313` and
  `1555117dd9e5b393cf5b92e10e603e1c5f8ba2bb`, recorded in
  `source/vendor/README.md`. Sampled XTM and packet-DMA files carry Broadcom
  DUAL/GPL notices; this does not establish redistribution rights for every
  source file, header, or dependency. No source was copied into this report or
  the public tree.

## The 19-import split

| Imports | Count | Finding | Required next evidence |
|---|---:|---|---|
| `bcmPktDma_Xtm*` packet-DMA calls | 15 | Corresponding implementations exist in the local BCM63168 family mirror, but they depend on Broadcom descriptor, channel, buffer, cache, and DMA definitions not established by the probe. | Review definitions and hardware semantics locally; establish descriptor layout, endian fields, DMA mask/addressing, ownership transitions, cache sync, ring wrap, and stop/reset behavior before adapting. |
| `BcmHalMapInterrupt`, `enable_brcm_irq`, `disable_brcm_irq` | 3 | These are legacy Broadcom interrupt-controller helpers. Their integer IDs and global mask semantics cannot be replaced by success-returning stubs. | Identify the actual XTM interrupt resources and controller mapping from lawful exact-SoC evidence, then use the Linux IRQ domain/device resource path. |
| `kerSysGetMacAddress` | 1 | This is platform board/MAC-allocation glue, not a generic XTM operation. The stock function takes a board allocation index. | Establish how the XTM interface obtains its assigned address from supported firmware/DT/NVMEM plumbing. Do not carry device MAC values or assume an allocation index. |

The comparison mirror is not a drop-in implementation: its later XTM/PktDma
interface changes descriptor-allocation signatures and the `XtmXmitAvailable`
arguments relative to the BCM63168 family source. Do not use the later mirror
to fill missing symbols without proving the target controller and ABI match.

## Ethernet and DSL consequences

The local board-parameter record for `963168MXH_17A` supports the presence of
an HS-SPI external-switch group and a separate memory-mapped group. It does
not settle switch silicon, CPU port, PHY-to-jack mapping, or MAC role. Keep the
DSA topology inactive until independent evidence identifies those details.

The XTM import inventory covers the runtime transport object probe. It does
not supply the absent `adsldd` PHY driver, `bcmxtmcfg` control implementation,
or legal PHY firmware. Resolve those source/provenance and ABI gaps separately;
do not reinterpret the 19 imports as the 82/31 stock-module imports.

## Next offline work

1. Preserve the pinned build and existing artifacts. The current local
   OpenWrt checkout is a separate build tree; do not treat its hashes as the
   handoff build hashes or rebuild without changed inputs.
2. Recover the private `hermes/xtm-6.18.54-preflight` research commit/logs if
   available. Commit `4dd24d42e7b052550a7d6fb7eaddad2f2a54b306` is not in this
   public checkout's object database.
3. For each DMA import, compare call-site contract with the exact family
   implementation and the pinned Linux DMA API. Design a real platform
   boundary before writing an adapter; retain the probe as a failing
   diagnostic until real code links.
4. Reconstruct the interrupt and MAC-address integration from exact platform
   evidence. Keep board values unresolved where evidence is missing.
5. Continue separate Ethernet switch and DSL control/PHY research. No router
   access, reset, reboot, UART, raw MTD, configuration change, module load, or
   flash is part of this work.

Status remains `PARTIAL-PORT`, `OFFLINE-ONLY`, and `NOT-FLASHABLE`.
