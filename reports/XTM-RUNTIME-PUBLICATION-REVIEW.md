# XTM component publication review

Scope: new feature-branch implementation and related tests/tools/reports.
The pinned local source inventory found the BCM63168-family `impl4` plus
PacketDMA `impl1` at `e2f23ddbb20bf75689372b6e6a5a0dc613f6e313`, and the later
comparison mirror at `1555117dd9e5b393cf5b92e10e603e1c5f8ba2bb`. Only the exact
family supplied the contracts implemented here; the comparison is not an ABI
substitute. Both trees remain external and unchanged.

| Files | Origin and license | Publication decision |
|---|---|---|
| `drivers/xtm/xtm_core.[ch]`, `xtm_dma.[ch]`, `Makefile` | Newly written GPL-2.0-only code; hardware layout/flag facts and functional API signatures are documented in the contract TSV. No vendor implementation body or header copied. | Source approved |
| `tests/test_xtm_core.c`, `tools/test-xtm-core.sh`, `tools/build-xtm-dma.sh` | Newly written GPL-2.0-only tests/build tools. | Source approved |
| `drivers/xtm/COPYING` | Verbatim GPL version 2 license text from the pinned kernel `LICENSES/preferred/GPL-2.0`; FSF copyright and permission to copy preserved. | License text approved |
| README, contract TSV, runtime/build reports, status updates | Original explanatory text and factual measurements; no device data or implementation excerpts. | Documentation/data approved |
| Source mirrors, stock modules, probe material and all generated `.ko`/logs | External source/build/research material with separate provenance/licensing/privacy boundaries. | Excluded from public Git |

The component uses GPL licensing independently of the top-level Apache-2.0
project license. No external vendor license is overridden. This is original
implementation informed by source inspection, not a claim of a clean-room
process. Full vendor dependency and binary redistribution approval remains
unsettled and is unnecessary for publishing this original component's source.

Local secret/content scanning and Git history review remain required before
each push. No scanner heuristic or legitimate copyright attribution is removed.
No firmware, MAC/serial, calibration, NVRAM, credential or key appears in the
new source/fixtures. Artifacts and full build logs are outside the repository.
