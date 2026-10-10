# enetsw RX and NAPI corrections

Scope: Linux 6.18.54 / pinned OpenWrt
`5edcc1c43cb97048b506168fbbe00538956796d6`. `BUILD-RESULT` and CPU-only tests;
SBG3300 OpenWrt runtime remains `NOT-TESTED`. DSL is deferred.

## Actual defects and implementation

New Linux delta `integration/schema-patches/0004-bcm6368-enetsw-rx-poll.patch`
and OpenWrt delivery patch `0010-bmips-enetsw-rx-poll.patch` correct:

- RX's do/while visited an unarmed descriptor even when the armed count or
  budget was zero. The loop now checks its bounded budget before access.
- A DMA length below FCS size underflowed before DMA sync/skb_put; an oversized
  length could exceed the mapped buffer. RX rejects lengths below an Ethernet
  header plus FCS or above the actual mapped buffer before subtraction/access.
  Existing error status flags also drop the frame and update error statistics.
- A zero-budget poll is TX-only. It now reclaims TX and returns without RX APIs
  or NAPI completion, as required by the [Linux NAPI contract](https://docs.kernel.org/networking/napi.html).
- Interrupts are restored only when `napi_complete_done()` returns true.
- TX completion previously read status after unlocking, when xmit could reuse
  the descriptor. Status is captured under the lock for error accounting.
- Descriptor ownership uses single status accesses and DMA read/write barriers.
  No register definitions, topology, channel ownership, or board enablement
  have been invented or changed.

These changes are original modifications to GPL-2.0-or-later upstream code;
existing kernel attribution is retained. No vendor implementation is copied.

## Actual callback tests

`tools/extract-enetsw-rx-poll-test.py` extracts the receive, reclaim and poll
functions plus descriptor definitions from the actual prepared C source.
`tests/test_enetsw_rx_poll.c` executes them with CPU-only kernel API doubles.
It tests lengths 0–17 and above the mapping, error flags, copybreak/zero-copy
lifetimes, allocation/skb-build failure, hardware ownership, ring wrap, empty
rings, TX-only polls, denied/successful NAPI completion, budget exhaustion, and
status overwritten by simulated descriptor reuse after unlocking.

Native GCC, Clang ASan/UBSan and static MIPS big-endian/o32 QEMU runs pass.
The pre-fix callback suite aborts with exit 134, preserving the regression
result. The first harness compile rejected an unused rmb API-double function;
it was replaced by a macro for old-source testing. Initial MIPS invocation
reported missing STAGING_DIR environment warnings; the correctly configured
repeat passes without them. These failed/intermediate runs remain private.

Test commands use `ENETSW_SOURCE` pointing to the actual candidate C file:

```sh
bash tools/test-enetsw-rx-poll.sh
CC=clang ENET_TEST_CFLAGS='-fsanitize=address,undefined -fno-omit-frame-pointer -g' bash tools/test-enetsw-rx-poll.sh
# With STAGING_DIR and the preserved OpenWrt cross compiler configured:
ENET_TEST_CFLAGS=-static ENET_TEST_EMULATOR=qemu-mips-static bash tools/test-enetsw-rx-poll.sh
```

## Compilation, ABI and integration

`tools/build-enetsw-validation.sh` copies the preserved source, applies or
verifies both real Ethernet deltas, and builds two fresh external modules.
W=1/-Werror C/compiler/modpost exits 0 twice, with zero warnings/errors.
Original .config, Module.symvers, vmlinux and UTS hashes verify unchanged.

| Artifact | Result |
|---|---|
| `bcm6368-enetsw.ko` | 113932 bytes; ELF32 MIPS BE/o32 |
| SHA256 (both builds) | `091acf5f6c90fc6f2bebe202343fc295817a4a95b93795e1562efafa396da7d0` |
| Vermagic | `6.18.54 SMP mod_unload BMIPS 32BIT` |
| Imports | 85; none missing from the real matching Module.symvers |
| Dependencies | No separate module dependencies in this build configuration |
| Runtime | `NOT-TESTED`; no device module loading |

Logs, input hashes and artifacts: local cache
`sbg3300-enetsw-validation/run-cNh674`. Earlier accepted modules remain intact.
All ten OpenWrt patches apply via git am to a separate fresh pinned checkout;
resulting source tree is `4769e1aa08793c94a990092080d6db094d67a30f`.
The delivered kernel patch equals the independently applied/tested Linux delta.
No final firmware image target was invoked. Hardware topology, boot, MAC and
DSA cascade blockers remain in the topology report.
