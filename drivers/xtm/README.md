# BCM63168 XTM ring component

`xtm_core.c` implements descriptor policy, queue capacity/FIFO accounting,
ownership checks, ring wrap and malformed-completion handling. The same C
code is executed by the host tests and linked into the kernel component.

`xtm_dma.c` provides real Linux coherent descriptor allocation, streaming
packet mapping/unmapping, ownership barriers, completion processing, local
statistics and bounded channel stop. It has no vendor headers, NBuff/FKB
classification shim, fabricated imports or platform-driver registration.
`sbg3300_xtm_dma.ko` is a ring support component, not the complete XTM netdev
or DSL runtime. There is no module initialization that accesses hardware.

The hardware format is the eight-byte, big-endian descriptor in the exact
BCM63168 family source: 16-bit length, 16-bit status, 32-bit bus address.
Lengths are restricted to 1..4095; unsupported FPM/multicast length flags are
rejected. TX uses one descriptor per copied linear packet. RX preserves raw
SAR status, validates length and FSTAT_ERROR, and returns an unmapped CPU-owned
buffer. Transport parsing, cell dispatch, bonding, FAP and scatter/gather are
not implemented by this component.

The future platform/netdev caller must configure a verified device DMA mask
and bus window (no wider than the descriptor's 32-bit address), exclusively
own the SAR resources, and provide the exact mapped channel and state-RAM
addresses. The component does not invent these resources or instantiate a
device. No DTS nodes are enabled by this work.

Administrative operations (`bind`, `start`, `stop`, `destroy`) are sleepable.
Submission and polling serialize with a spinlock. Ring lifetime remains the
caller’s responsibility: synchronize users, IRQ and NAPI before destruction.
Mappings cannot be destroyed while software says the channel is running or
the hardware ENABLE bit is set. A stop timeout blocks further submission and
keeps the ring and mappings alive. A ring that was never bound may be cancelled
safely because its DMA address was never programmed into a controller.
Stop is terminal: destroy and allocate a new ring for another session. The
optional final statistics output from destruction includes cancelled buffers.

Coherent descriptors still require ordering: packet mapping/address writes
precede OWN publication through `dma_wmb`; completion observes OWN clear and
uses `dma_rmb` before buffer unmapping. Streaming mappings are created once per
packet and unmapped before CPU access, so no mapping is retained across CPU
ownership and no ad hoc MIPS cache-flush helper is used. See the official
[DMA API guide](https://docs.kernel.org/core-api/dma-api-howto.html).

Run `bash tools/test-xtm-core.sh`. For host sanitizers, use
`CC=clang XTM_TEST_CFLAGS='-fsanitize=address,undefined -g'` with that command.
Cross-build instructions and exact results are in the runtime build report.

## Provenance and publication

All implementation in this directory and its tests is newly written project
code licensed GPL-2.0-only. No vendor implementation body or header was copied.
The interface facts and API signatures are traced to the pinned local family
source in `reports/XTM-BCM63168-CONTRACTS.tsv`. Sampled vendor files have DUAL/GPL
notices, but the full dependency tree has unsettled redistribution rights;
those files remain outside this repository. This is not a claim of a clean-room
process or a grant of rights for the external mirrors.

## PTM frontend

`xtm_ptm_register` builds a netdev only for an owning parent with verified
resources/MAC/DSL configuration. IRQ/NAPI/BQL, refill, statistics and teardown
are implemented. See `xtm_ptm.h` and the PTM build report for lifetime rules.
There is no automatic platform binding, SAR/FAP ownership acquisition or DSL
PHY/control implementation. Keep hardware inactive until those contracts exist.
