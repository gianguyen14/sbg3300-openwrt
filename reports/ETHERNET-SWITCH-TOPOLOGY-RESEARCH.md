# SBG3300 Ethernet and switch topology research

Date: 2026-10-10. Scope: source reconstruction and offline validation for
Zyxel SBG3300-N000 board ID `963168MXH_17A`. OpenWrt baseline
`5edcc1c43cb97048b506168fbbe00538956796d6`, Linux 6.18.54,
`bmips/bcm63268`. DSL is deferred. The initial source review was offline;
owner-authorized read-only SSH and a LAN1/LAN2 cable A/B/A test were completed
later on 2026-10-10 and are recorded below. No router configuration was
changed. The research fixture is disabled and cannot be used as a hardware
configuration.

## Result

The source and boot evidence now supports a coherent two-switch topology:
BCM63168 SoC switch port 6 is configured as a 1-Gbit/s RGMII external-switch
link, and BCM53125 port 8 is the likely IMP/cascade endpoint. The exact-family
stock configuration selects HSSPI bus 1, chip-select 0, SPI mode 3, at 781 kHz.
The same-board-ID bootlog reports VLAN 1 with external ports 1–4 untagged and
port 8 tagged. Linux 6.18's BCM53125 profile also identifies port 8 as its IMP
port. Together, those are strong board-specific support for a port-6↔port-8
cascade, while the precise RGMII delay/electrical mode and Linux DSA behavior
remain unverified.

The external silicon identity is verified for a bootlog reporting the same
firmware board ID as the live stock report: BCM53125. The public log does not
show a PCB silkscreen revision; `963168MXH_17A` is a firmware board identifier.
The exact-family boardparms source has a C3 `#if 1` branch and a C2 `#else`
alternative. Bootlog bitmaps match the C3 branch, but equivalence between the
public source mirror and Zyxel's running firmware image is not established.

Owner-assisted A/B/A testing now verifies the physical LAN 1 jack maps to
stock netdev `eth0` and LAN 2 maps to `eth1`. This does not by itself identify
the PHY or external-switch port behind either netdev. The LAN 1 to stock
logical switch-index-4 chain is supported by the stock boot observation and
family-source decode; `eth1`'s logical switch index is not captured. LAN 3,
LAN 4, and Ethernet WAN were not tested. WAN-to-SoC-PHY mapping, DSA labels,
reset GPIO, RGMII timing, and MAC provisioning remain unresolved. DSL remains
deferred.

## Evidence classes and confidence

This report uses the repository policy in `docs/EVIDENCE-POLICY.md`. The
additional topology status words are defined as follows: `VERIFIED` means a
direct source or observation states the fact; `SUPPORTED` means independent
board-specific observations align but a physical/software-link detail is
missing; `INFERRED` means a plausible conclusion with stated assumptions; and
`UNKNOWN` means the evidence cannot decide it. A status does not upgrade stock
behavior into Linux 6.18 behavior.

| Claim | Status | Evidence and boundary |
|---|---|---|
| BCM63168D0 and external BCM53125 appear in the public SBG3300 bootlog | `VERIFIED` | `STOCK-BOOT-LOG`: the log prints board ID `963168MXH_17A`, BCM63168D0 and external switch ID 53125 together. It does not prove the PCB layout. |
| The live stock device reports board ID `963168MXH_17A` | `VERIFIED` | `LIVE-DEVICE`: sanitized prior SSH report. Same ID ties the live observation to the public log at firmware board-ID level, not physical board artwork. |
| Boardparms C3 branch uses SoC port map `0x58`; port 3 has PHY ID 4, port 4 is `TMII_DIRECT|0x14`, and port 6 is `RGMII_DIRECT|EXTSW_CONNECTED` | `VERIFIED` | `EXACT-BOARD-SOURCE`: public Broadcom mirror `boardparms.c:2878–2928`, commit `e2f23ddbb20bf75689372b6e6a5a0dc613f6e313`; definitions in `boardparms.h:462–466, 537–599`. Source build equivalence remains unproven. |
| The stock bootlog selects the C3 boardparms configuration | `SUPPORTED` | Log unit-0 `config_pbmp=0x58` and unit-1 `phypbmp=0x1e` match the source's C3 branch. The C2 alternative is `0x50`/`0x1f` and swaps the port-4/port-6 interface roles. This is a bitmap cross-check, not a firmware hash comparison. |
| BCM53125 is controlled through HSSPI bus 1 CS0 in the family driver contract | `SUPPORTED` | `FAMILY-SOURCE`: exact entry selects `HS_SPI_SSB_0`; `bcmswaccess.c:618–640` maps SSB0 to ID 0; `bcmenet.c:6786–6802` reserves HSSPI bus 1/CS0, mode 3, 781 kHz. `LIVE-DEVICE` observed `spi1.0` and a generic HSSPI child. Together with the bootlog switch discovery, this supports the stock software path but does not expose PCB traces. |
| The SSB5 overlay configures an additional HSSPI SS5 pin function | `VERIFIED` | `EXACT-BOARD-SOURCE`: `setup.c:1444–1456` sets the SS5 GPIO mode when the overlay is present. The active Ethernet configuration still selects SSB0. The source comment at `boardparms.c:2923` describes SSB5 as an alternative after specified MDIO resistor changes. What else, if anything, uses the extra SS5 pin on the physical board is `UNKNOWN`. |
| External BCM53125 switch has PHY ports 1–4 and boardparms map `0x1e` | `VERIFIED` | `EXACT-BOARD-SOURCE`: the external HSSPI group lists PHY IDs 1–4 at `boardparms.c:2921–2928`; `STOCK-BOOT-LOG` reports unit-1 bitmap `0x1e`. No per-jack labels are encoded. |
| BCM53125 port 8 is the cascade/IMP connected to SoC port 6 | `SUPPORTED` (high confidence) | Exact-board port 6 is marked external-switch RGMII; same-board-ID boot output shows port 8 tagged while ports 1–4 are untagged in default VLAN 1; Linux 6.18's BCM53125 profile names `imp_port = 8` (`b53_common.c:2883–2891`). These independently align. Neither source shows the PCB net or proves Linux DSA runtime. |
| SoC port 3 uses the internal PHY at ID 4 | `VERIFIED` as boardparms encoding | `EXACT-BOARD-SOURCE` gives `BP_PHY_ID_4`; pinned `bcm63268.dtsi:564–607` describes SoC MDIO PHY 4 and its GPHY reset. Exact board wiring of that PHY to a connector is unknown. |
| SoC port 4 is a fixed 100-Mbit/s full-duplex MAC-to-PHY MII connection with encoded ID `0x14` | `VERIFIED` as boardparms encoding | `TMII_DIRECT` definitions set forced 100FD, MAC-to-PHY and MII; low PHY ID bits of `0x14` are 20. Whether the stock Linux build exposes this endpoint as PHY address 20, and its board function, are `UNKNOWN`. |
| Ethernet WAN is SoC port 3 / PHY 4 | `INFERRED` (medium-low) | Product docs establish a separate ETHWAN connector; the SoC map has port 3/PHY4 outside the four-port external group, and the live stock logical map has `eth4→11` (internal port 3 under the family port-index algorithm). No exact board source labels it WAN or maps it to that connector. |
| Physical LAN 1 jack ↔ stock netdev `eth0` | `VERIFIED` | `LIVE-DEVICE`: owner-confirmed A/B/A cable placement. With the cable at LAN 1, `eth0` carrier was up and `eth1` down; at LAN 2, `eth0` was down and `eth1` up; after return to LAN 1, the original state returned. No other cable was moved. This verifies the stock jack-to-netdev correlation only. |
| Physical LAN 2 jack ↔ stock netdev `eth1` | `VERIFIED` | `LIVE-DEVICE`: same owner-confirmed A/B/A sequence. Carrier and counter observations are detailed below. This does not identify a PHY or switch-port number. |
| LAN 1 ↔ external BCM53125 port 4 | `SUPPORTED` | The A/B/A test verifies LAN 1 ↔ `eth0`; prior live stock boot evidence maps `eth0` to logical switch index 4, and the exact-family source interprets the external low indices as switch ports. Exact running-binary equivalence and PCB trace are not proven. |
| LAN 2 / `eth1` ↔ a specific BCM53125 PHY port | `UNKNOWN` | The A/B/A test verifies LAN 2 ↔ `eth1`, but no live logical switch index for `eth1` was captured. Do not assign the otherwise plausible remaining port 3 by elimination. |
| LAN 3, LAN 4, and Ethernet WAN ↔ stock netdev/PHY/switch port | `UNKNOWN` | No cable test was made on these jacks. LAN 3 and Ethernet WAN were physically occupied and left untouched; LAN 4 was not tested. |
| Any stock `ethN` name equals a physical jack number | `UNKNOWN` generally | `eth0` and `eth1` are now individually correlated by A/B/A, but the remaining stock interfaces are still not mapped to jacks. |
| External switch uses Linux `b53_spi`, DSA, or the same tag format as stock | `UNKNOWN` for runtime | `UPSTREAM` has matching B53 SPI support and exact BCM53125 chip profile. The stock family source selects a vendor type-2 tag value/format not yet shown byte-compatible with the standard Linux B53 DSA protocol. |

## Annotated topology reconstruction

```text
  SBG3300-N000 ETHERNET WAN jack
       ? physical wiring / role unresolved
       ? candidate: SoC integrated port 3, internal PHY ID 4 [INFERRED]
       |
       +-------------------------------+
                                       |
       BCM63168D0 internal switch      |
       port 3: PHY_ID_4 [VERIFIED] ----+---- physical connector unknown
       port 4: TMII_DIRECT|0x14        +---- 100FD MII, endpoint/role unknown
       port 6: RGMII_DIRECT + EXTSW ---+---- RGMII ---- BCM53125 port 8 [SUPPORTED]
                                       |                 IMP/cascade, high confidence
       port 8: internal DSA CPU port  |                     |
          fixed 1G to enetsw MAC/DMA   |                     +-- ports 1–4 PHYs
          [UPSTREAM SoC DTS contract]   |                         [VERIFIED map]
          [board node disabled]        |                         | VLAN 1 PVID/untag
                                       |                         | [STOCK-BOOT-LOG]
  BCM63168 enetsw DMA/MAC -------------+                         +-- four LAN jacks
  RX/TX DMA channels 0/1; IRQ names,                              [group INFERRED;
  clocks, resets in pinned SoC DTS                                order UNKNOWN]
  [UPSTREAM; disabled for SBG]

  Control plane:
  BCM63168 HSSPI (`spi1`, base 0x10001000) -- bus 1 / CS0 -- BCM53125
     mode 3, 781 kHz [EXACT-FAMILY + LIVE spi1.0; SUPPORTED stock path]
     CS5 GPIO overlay also enabled [VERIFIED pinmux request; purpose UNKNOWN]

  VLAN 1 in the public same-board-ID bootlog: external ports 1,2,3,4
  untagged/PVID 1; port 8 tagged. This is boot-time switch output, not a
  complete final stock VLAN table or OpenWrt WAN/LAN policy.
```

The internal `switch0` port 8 ↔ SoC Ethernet MAC relation is an upstream
BCM63268 device-tree contract, not a SBG3300 activation result. The external
port 8 ↔ internal port 6 relation is a strong `INFERENCE` from the exact-board
port-6 setting, stock VLAN tagging, and Linux's BCM53125 IMP-port profile. The
diagram intentionally separates those two links.

## Exact-board source trace

Source: public mirror
[`nomis/bcm963xx_4.12L.06B_consumer`](https://github.com/nomis/bcm963xx_4.12L.06B_consumer),
commit `e2f23ddbb20bf75689372b6e6a5a0dc613f6e313`. This is a public family
source mirror, not an authenticated Zyxel build export. The reviewed source
remains outside this repository; no vendor implementation was copied.

- `shared/opensource/boardparms/bcm963xx/boardparms.c:2878–2928`: exact board
  entry. Active C3 branch has MMAP map `0x58` (bits 3, 4, 6); port 3 is
  `BP_PHY_ID_4`; port 4 is `TMII_DIRECT|0x14`; port 6 is
  `RGMII_DIRECT|EXTSW_CONNECTED`. External group is HSSPI SSB0, map `0x1e`,
  PHY IDs 1–4.
- `boardparms.c:2929–2945`: C2 alternative. It uses internal map `0x50`,
  puts RGMII/external-switch on port 4 and TMII on port 6, and external map
  `0x1f`. The bootlog bitmaps match C3, not this alternative.
- `shared/opensource/include/bcm963xx/boardparms.h:462–466` defines PHY ID 4;
  `:537–599` defines MAC connection, MII/RGMII modes, `EXTSW_CONNECTED`, and
  `IsWanPort`. Port 3's value has no WAN flag. Port 4's `0x14` encoding is not
  a board-role label.
- `boardparms.h:296–301` defines the SSB external-CS overlays. The exact entry
  includes `BP_OVERLAY_HS_SPI_SSB5_EXT_CS`, but its selected Ethernet access
  type is SSB0. `kernel/linux/arch/mips/bcm963xx/setup.c:1444–1456` shows the
  overlay's effect: enable the SS4–SS7 pin mode, including SS5. It does not
  select a chip for that CS.
- `bcmdrivers/opensource/net/enet/shared/bcmswaccess.c:618–640` maps an HSSPI
  SSB selector to `MBUS_HS_SPI` and the numeric select; SSB0 becomes 0.
  `shared/opensource/include/bcm963xx/bcmSpiRes.h:117–119` defines high-speed
  SPI bus number 1.
- `bcmdrivers/opensource/net/enet/impl4/bcmenet.c:6786–6802` reserves bus 1,
  selected CS0, `SPI_MODE_3`, 781000 Hz; it sets stock switch tag mode to
  `BRCM_TYPE2`. `:6982–6993` reads the chip ID and enables Broadcom header mode
  on the IMP port during stock driver init. This is source behavior, not a
  command run against the live router.
- `bcmenet.c:6736–6750` consolidates the two switch maps: external-switch port
  bits occupy their low logical indices; remaining SoC ports are shifted by 8;
  the internal port marked `EXTSW_CONNECTED` is omitted as an end port.
  `:1144–1215` walks that map to create virtual ports and chooses switch unit
  and physical port. This explains why stock indices are not front-panel labels.
  Build macros and exact binary equivalence are not proven, so this algorithm
  is a family-source explanation, not a guaranteed decode of every live `ethN`.
- `bcmenet.c:1403–1405` marks a virtual interface WAN only when the encoded PHY
  ID has the WAN flag. The exact SBG C3 port-3 value is plain PHY ID 4, which
  does not identify the separate ETHWAN connector in this table.
- `bcmdrivers/opensource/net/enet/shared/bcmenet.h:109–122,170–171` defines the
  type-2 frame header, `BRCM_TYPE2=0x888A`, and a four-byte total inserted
  header. It is a distinct encoding, not a six-byte length delta.

## Bootlog, HSSPI, switch PHYs and MDIO ownership

The [public SBG3300 bootlog](https://jirkabalhar.cz/posts/hack-router/zyxel-sbg3300-bootlog.html)
prints board ID at page line 54, BCM63168D0 and switch ID 53125 at lines 38–39,
and the 4.12L.06B release/MDK startup at lines 402–414. It says the MDK forces
the 53115 driver for detected 53125 silicon, then prints unit-0
`phy_pbmp=0x18/config_pbmp=0x58` and unit-1 `phypbmp=0x1e`. Treat that as a
stock MDK compatibility selection. Linux `b53` already has a BCM53125 chip
profile; there is no evidence to identify it as BCM53115 in Linux.

Bootlog lines 425–456 print the initial VLAN 1 memberships: external port 8 is
tagged, ports 1–4 are untagged and have PVID 1. The report uses only those
printed boot messages. No register-selector, switch utility, or selector
command was run. The log page contains private identifiers unrelated to this
research; none are reproduced here.

The exact-family SSB0 selection and driver reservation resolve the stock
software configuration to HSSPI bus 1 / CS0 / mode 3 / 781 kHz. Prior
`LIVE-DEVICE` sysfs data shows `spi1.0` and a generic HSSPI binding, consistent
with the source. The board's separate SS5 overlay requests the SS5 pinmux in
family setup code. An adjacent comment says SSB5 is an alternative after
installing specified MDIO resistors; the active entry does not select SSB5.
The purpose of enabling SS5 while selecting SSB0 remains unknown, but it is not
evidence that this BCM53125 is on CS5.

The boardparms external-switch group is HSSPI and maps the four external PHYs
as 1–4. Linux's generic `mdio_ext` is a separate empty bus in the pinned SoC
DTS. Do not bind the BCM53125 both as an HSSPI SPI child and an MDIO PHY/device.
That could create duplicate device discovery and overlapping PHY scans. The
SoC internal MDIO mux has a separate `mdio_int` containing PHYs 1–4; that does
not prove the external switch PHYs are on the SoC MDIO bus. With B53 over SPI,
external switch PHY access belongs to the B53 register/PHY operations.

The board source provides no external switch reset GPIO, power/reset sequence,
strap reading, or RGMII delay. Stock `bcmenet.c` has an `ethsw_reset` call only
under `NO_CFE`; this does not establish a Linux reset requirement for the
normal boot path. Keep reset ownership unresolved. Don't add `reset-gpios`,
`phy-mode`, `fixed-link`, DSA link references, or RGMII delay properties from a
sibling design.

## Stock logical ports and WAN/LAN hypotheses

`LIVE-DEVICE` evidence in `LIVE-READONLY-2026-10-10.md` maps stock logical
interfaces to driver switch indices as follows. These are not silkscreen jack
numbers:

| Stock netdev | Stock logical switch index | Family-source interpretation, conditional on same driver build |
|---|---:|---|
| `eth0` | 4 | External-switch index 4 |
| `eth2` | 2 | External-switch index 2 |
| `eth3` | 1 | External-switch index 1 |
| `eth4` | 11 | Consolidated index 8+3; candidate internal port 3 |
| `eth5` | 12 | Consolidated index 8+4; candidate internal port 4 |
| `eth1` | not captured | Unknown |

The family driver algorithm supports the offset decode (`bcmenet.c:6736–6750,
1144–1215`), but the exact stock binary's source/build flags are unavailable.
The live report also notes `eth4.1` under PPP. That does not prove the discrete
Ethernet-WAN jack, a final switch VLAN, or even that the runtime path is
Ethernet-only; DSL/XTM is not part of this milestone.

| Hypothesis | Status | Reason |
|---|---|---|
| SoC port 6 ↔ BCM53125 port 8 | `SUPPORTED`, high confidence | Boardparms port 6 is explicitly RGMII/direct/external-switch; same-board bootlog tags port 8; Linux profile's BCM53125 IMP port is 8. PCB net and delay not observed. |
| BCM53125 ports 1–4 are a LAN-facing group | `SUPPORTED` as a group | Exact map has PHY 1–4 and bootlog VLAN 1 makes those ports untagged/PVID 1. Exact front-panel correspondence is not given. |
| LAN 1 maps to stock `eth0` | `VERIFIED` | Owner-assisted A/B/A carrier observation; details below. |
| LAN 2 maps to stock `eth1` | `VERIFIED` | Owner-assisted A/B/A carrier observation; details below. |
| LAN 1 is BCM53125 PHY/port 4 | `SUPPORTED` | Physical jack maps to `eth0`; stock boot evidence maps `eth0` to logical switch index 4; exact-family source supports interpreting it as external port 4. The source-to-running-binary and PCB net are not proven. |
| LAN 2 is BCM53125 PHY/port 3 | `UNKNOWN` | `eth1`'s stock logical switch index is absent from captured boot evidence. Port 3 is not assigned by elimination. |
| SoC port 3 / PHY 4 is Ethernet WAN | `INFERRED` | Separate ETHWAN connector is documented and stock `eth4` maps to candidate internal port 3 under the family algorithm. No board source WAN label or safe link-to-jack correlation. |
| SoC port 4 / encoded PHY 20 is the fifth Ethernet jack or switch WAN | `UNKNOWN` | Boardparms only gives a direct MII 100FD endpoint. It does not describe its connector or product role. |
| `eth4.1` is the separate ETHWAN jack | `UNKNOWN` | PPP/VLAN layering without final VLAN membership or physical link correlation is insufficient. |

### Physical jack mapping summary

| Physical jack | Stock netdev | SoC path | BCM53125 port | Evidence | Confidence |
|---|---|---|---|---|---|
| ETHERNET 1 | `eth0` | Candidate external-switch path through SoC port 6 | Port 4 supported | Owner-assisted A/B/A verifies jack↔netdev; live boot maps `eth0` to logical index 4; exact-family source interprets the external index as port 4 | `VERIFIED` jack↔netdev; `SUPPORTED` port decode |
| ETHERNET 2 | `eth1` | Unknown | Unknown | Owner-assisted A/B/A verifies jack↔netdev; no stock logical index for `eth1` was captured | `VERIFIED` jack↔netdev; PHY path `UNKNOWN` |
| ETHERNET 3 | Unknown | Unknown; external-switch group is only a group-level hypothesis | Unknown | Owner reports this jack is occupied; it was not tested | `UNKNOWN` |
| ETHERNET 4 | Unknown | Unknown; external-switch group is only a group-level hypothesis | Unknown | Jack was not tested | `UNKNOWN` |
| ETHERNET WAN | Unknown | Candidate SoC port 3 / PHY 4 | Unknown | Jack remained occupied and untouched; candidate derives from boardparms and logical-index interpretation, not jack observation | Jack mapping `UNKNOWN`; candidate SoC path `INFERRED` |

Product documentation labels ETHERNET WAN separately from ETHERNET 1–4 and
describes a fifth Ethernet port that can be reassigned to LAN under specified
stock use. This confirms port-role flexibility in product software, not
board-level wiring or the OpenWrt DSA policy. MAC provisioning is also
unresolved: the family driver reads factory/NVRAM-derived MAC data, but no
public, lawful Linux 6.18 nvmem source/offset contract was found. No device MAC
or offset is included here.

### Owner-assisted LAN 1 / LAN 2 A/B/A test

Date: 2026-10-10. Evidence: `LIVE-DEVICE`, read-only stock SSH through the
owner's existing `sbg3300` command. The owner confirmed LAN 1 was the cable's
starting jack, moved that same cable to LAN 2, then returned it to LAN 1. The
owner separately confirmed the cable was on LAN 2 before the 17:16:45 UTC
snapshot and back on LAN 1 before the 17:21:58 UTC snapshot. LAN 3 and Ethernet
WAN remained untouched. The test did not change router configuration or send
test traffic.

| State | Physical placement | `eth0` | `eth1` | Guard observations |
|---|---|---:|---:|---|
| A, 17:12:04 UTC | LAN 1 | carrier up | carrier down | Earlier read-only baseline; SSH responsive |
| B, 17:16:45 UTC | LAN 2 | carrier down | carrier up | Owner confirmed move occurred before this snapshot; route remained on `ppp2.1` |
| B stability, 17:19:12 and 17:19:16 UTC | LAN 2 | carrier down | carrier up | Two snapshots retained the same carriers; SSH responsive; default route unchanged |
| A2, 17:21:58 UTC | LAN 1 | carrier up | carrier down | Fresh `sbg3300` SSH succeeded; full-interface snapshot and route check completed |
| A2 stability, about 3 seconds later | LAN 1 | carrier up | carrier down | `eth0` remained up and `eth1` down; `eth2` and `eth4` remained up; route remained on `ppp2.1` |

The A2 all-interface snapshot showed `eth0` up, `eth1` down, `eth2` up,
`eth3` down, `eth4` up, and `eth5` down. The bridge, PPP, VLAN, tunnel,
loopback, Wi-Fi, and `bcmsw` entries were also inspected through sysfs; the
route list was unchanged, and `eth0`–`eth5` reported no RX/TX errors. Absolute
counters for unrelated interfaces are omitted from this public report as
private runtime telemetry. The A2 check took a second short snapshot of the
relevant interfaces; `eth0` remained up, `eth1` remained down, and their
counters behaved consistently with those link states.
Read-only sysfs `dev_port` and `phys_port_name` attributes were unavailable
for both `eth0` and `eth1`, so this metadata did not identify a PHY or switch
port. `dev_id`/interface-index values are not physical switch-port evidence.

The carrier state reversed with the cable placement in both directions and
returned to the original state in A2. This is direct stock runtime evidence
for LAN 1 ↔ `eth0` and LAN 2 ↔ `eth1`; both jack-to-netdev mappings are
`VERIFIED`. It does not prove that either interface is a direct PHY netdev or
identify `eth1`'s logical switch index. The stock boot's `eth0`→index-4
observation plus family-source interpretation makes LAN 1→external port 4
`SUPPORTED`, not `VERIFIED`.

The stock kernel is Linux 2.6.30 on MIPS32/o32. Its upstream
`struct net_device_stats` uses native `unsigned long` fields for byte and
packet counts, so a 32-bit counter can wrap at 2³² when that API supplies the
reported statistics. For example, the captured `eth0` TX byte counter changed
from 3,816,604,641 to 601,577,519 across A→B. Interpreting one wrap gives a
modulo delta of 1,079,940,174 bytes. A later `eth4` RX decrease also fits one
modulo wrap. These decreases are not evidence of lost traffic; the precise
stock driver's statistics source is not established for every interface.
The kernel field definition is available in the [Linux v2.6.30 netdevice.h
source](https://github.com/torvalds/linux/blob/v2.6.30/include/linux/netdevice.h#L2389-L2400).

No active LAN 3 or WAN cable was touched. `ppp2.1` remained the route interface
throughout. The A/B/A procedure disconnected the other computer from LAN 1
while its cable was connected to LAN 2. The owner then returned that cable to
LAN 1; application-level connectivity on the other computer was not separately
tested. No SSH interruption or router configuration change was observed.

## Linux 6.18.54 and OpenWrt integration contract

The pinned `target/linux/bmips/dts/bcm63268.dtsi` at OpenWrt commit
`5edcc1c43cb97048b506168fbbe00538956796d6` defines the SoC-side contract:

- `:467–499` declares `brcm,bcm63268-enetsw`, three DMA register ranges,
  RX/TX DMA0 IRQ names, GMAC/Roboswitch/EPHY/GPHY clocks, ENETSW/EPHY resets,
  switch power domain, RX channel 0/TX channel 1, and a default disabled state.
  This is the upstream MAC/DMA frontend contract, not proof of board activation.
- `:533–555` declares the internal BCM63268 DSA switch and its port 8 CPU link
  to the enetsw MAC as 1-Gbit full duplex. The default CPU link does not encode
  external BCM53125 cascade wiring.
- `:558–615` declares internal PHYs 1–4 and reset timing, plus an empty
  `mdio_ext` child. It does not prove which of those PHYs are routed on this
  board.
- `:367–384` declares BCM6328 HSSPI at `0x10001000`, IRQ, clocks and reset,
  disabled. Pinctrl defines explicit SS4–SS7 groups but no separate CS0 group;
  do not invent CS0 pinmux from those siblings.

Linux 6.18.54's DSA B53 SPI match table contains `brcm,bcm53125`
(`drivers/net/dsa/b53/b53_spi.c:335–345`). The B53 BCM53125 chip data sets
`imp_port = 8` (`b53_common.c:2883–2891`). These make the driver family
available; no SBG3300 DSA tree has been activated. The upstream B53 DSA driver
and `bcm6368-enetsw` already have compile coverage in
`PRE-FINAL-ENGINEERING.md`; those are `BUILD-RESULT`, not a board runtime
result.

The external path must not be declared twice. If a later candidate confirms
the cascade, the DSA graph needs the SoC internal switch's port 6 linked to the
external BCM53125's port 8; the SoC internal port 8 remains the CPU conduit to
the MAC/DMA. DSA CPU/cascade links require the correct `phy-mode`/fixed-link
or managed link contract. Exact RGMII mode and delay owner are not known, so
those properties and both DSA link references remain omitted.

There is also a data-plane format issue to resolve before expecting stock-like
forwarding. The family source sets type-2 header value `0x888A` with a 4-byte
total inserted header (`bcmenet.h:109–122,170–171`). Upstream B53's default
protocol for BCM53125 is `DSA_TAG_PROTO_BRCM` (`b53_common.c:2495–2524`), whose
wire layout is a 4-byte Broadcom tag after the MAC source address
(`net/dsa/tag_brcm.c:44–50,135–145`). Equal byte count does not establish equal
field encoding: source code currently supports a stock-vs-DSA tag-format
mismatch hypothesis. No packets were captured and no B53 tag adaptation is
justified. Do not relabel the BCM53125 as 53115 to imitate the stock MDK
workaround.

For Ethernet WAN/LAN after the graph and tagging are proven, OpenWrt should use
DSA user ports and explicit bridge/VLAN policy. The port labels, bridge
membership, VLAN IDs, CPU tagging, PVIDs, and any dedicated WAN port must come
from board-specific wiring and product behavior, not from the sibling VG-8050
or Sagem DTS examples. No network configuration is added now.

## Candidate DTS and test work

Added `integration/dts/sbg3300-bcm53125-OFFLINE-ONLY.dts`. It is explicitly an
evidence fixture, not part of the OpenWrt patch series or product DTS. It adds
one disabled `brcm,bcm53125` child at HSSPI CS0 with source-backed mode 3 and
781 kHz, declares only raw ports 1–4 and 8, and omits all unproven links,
labels, PHY handles, tag protocol, reset, and MAC data. HSSPI, the SoC Ethernet
MAC, internal DSA switch and MDIO nodes remain disabled.

`tools/check-offline-dtb.py --ethernet-candidate` enforces that conservative
contract and rejects activation, duplicate MDIO binding, wrong CS/frequency,
invented port labels, or adding unresolved DSA/link/reset/tag data.
`tools/validate-pre-final-dts.sh` compiles and round-trips both the prior
SAR-resource fixture and the new Ethernet fixture, runs meta-schema and full
`dt-validate`, and checks empty diagnostics. It tolerates an exact reverse
patch match when schema deltas already exist in the preserved prepared kernel
tree; partial or drifted patch application still fails.

Results on pinned OpenWrt/Linux 6.18.54 source:

| Validation | Result |
|---|---|
| Native Python unit tests | `python3 -m unittest discover -s tests`: 22 passed |
| Candidate DTC compile and DTB→DTS round-trip | Pass, zero diagnostics |
| Existing board fixture DTC compile and round-trip | Pass, zero diagnostics |
| `dt-doc-validate` for selected bindings | Pass, zero diagnostics |
| Combined `dt-mk-schema` + `dt-validate` on board and candidate | Pass, zero diagnostics |
| Offline candidate contract | Pass; HSSPI/switch/SoC switch/MAC/MDIO disabled; DSA endpoint omitted |
| Candidate DTB SHA256 | `d3e7522c76ace2a0fb567c3f0fc6178b45648b171db655d4f9faa7f74f10ec91` |
| Existing board fixture DTB SHA256 | `3be99ff1c7e4962384cd292adfd408cace5439625c381026619f60946a99751d` |
| Existing Ethernet C module compile/modpost | Not repeated: no kernel C, Kconfig, or runtime DTS input was changed. Prior artifact coverage remains in the build report. |
| Hardware/runtime | Stock LAN 1/LAN 2 jack-to-netdev A/B/A tested; OpenWrt Ethernet/DSA runtime not tested |

This change adds source-contract tests and an inert evidence fixture; it does
not implement or claim a working Ethernet driver path. No sibling-board DTS
values were copied into the product DTS. Existing XTM/PTM code, tests, reports,
and successful build artifacts were left intact. No final firmware image was
built.

## Exact blockers and next evidence

Offline public source review is exhausted for the specific board-level facts
below. The evidence needed is actionable and bounded:

1. **RGMII endpoint, delay ownership, clock direction, and reset/strap state.**
   Needed: an SBG3300-N000 schematic/netlist for PCB revision matching the
   board ID, a public board-specific boot/init source that states the same
   values, or owner-provided unpowered board inspection identifying the
   SoC-port-6 nets and BCM53125 port-8 nets. This decides `phy-mode`, delay
   properties, fixed link and reset ownership. Do not use register selectors
   or probe live signals without separate approval.
2. **Remaining physical ETHERNET jack ↔ switch-port mapping.** LAN 1↔`eth0`
   and LAN 2↔`eth1` are now `VERIFIED` by owner-assisted stock A/B/A carrier
   observations. Needed for further mapping: equivalent owner-authorized
   testing of LAN 3/LAN 4 only when their service impact is acceptable; the
   physically occupied LAN 3 and WAN were not touched in this pass. `eth1`'s
   stock switch index and LAN 2's BCM53125 PHY remain unknown. Do not infer
   these from sibling boards or port-number elimination.
3. **Full VLAN membership and WAN mode.** Needed: a published/read-only stock
   status interface whose implementation is confirmed not to write registers,
   or owner-provided sanitized output of such an interface. Boot-time VLAN 1
   does not show final WAN/VLAN state. No `/proc/switch` selector or unknown
   `ethswctl` command is approved by this research.
4. **Stock type-2 tag bytes vs Linux DSA BRCM tag.** Needed: authoritative
   protocol documentation or a lawful sanitized frame capture from stock
   forwarding, collected with a separately approved passive method. Compare
   tag opcode/port bits and header placement before considering an upstream
   DSA tag change.
5. **MAC address source.** Needed: public board-specific nvmem/factory-data
   layout or a supported stock export contract that exposes only the
   provisioning mechanism, not any address values. Until then, no `mac-address`
   or NVRAM offset should be added.

The owner-authorized stock A/B/A cable test was completed only on LAN 1 and
LAN 2. No OpenWrt DSA/forwarding test, module loading, boot, router
configuration change, reset, flash access, or RGMII probing occurred. The
Ethernet, switch, and MDIO Device Tree nodes remain disabled; this stock test
does not establish Linux 6.18 runtime behavior.

## Source inventory

- `STOCK-BOOT-LOG`: [SBG3300 public CFE/Linux bootlog](https://jirkabalhar.cz/posts/hack-router/zyxel-sbg3300-bootlog.html).
- `FAMILY-SOURCE`: [Broadcom 4.12L.06B public mirror, exact board entry](https://github.com/nomis/bcm963xx_4.12L.06B_consumer/blob/e2f23ddbb20bf75689372b6e6a5a0dc613f6e313/shared/opensource/boardparms/bcm963xx/boardparms.c#L2878-L2945), and [HSSPI access mapping](https://github.com/nomis/bcm963xx_4.12L.06B_consumer/blob/e2f23ddbb20bf75689372b6e6a5a0dc613f6e313/bcmdrivers/opensource/net/enet/shared/bcmswaccess.c#L618-L640). Source redistribution/build equivalence is not represented as approved.
- `PRODUCT-DOCUMENTATION`: [Zyxel SBG3300-N series user guide](https://prodotti.zyxel.it/USERSGUIDE/ZYXSBG-3300.pdf) and [Zyxel service-provider SBG sales guide](https://www.zyxel.com/library/assets/tech-library/Quick-Sales-Guide/Service-Provider-SBG.pdf). A mirror of the user guide describes the fifth Ethernet port's alternate LAN use; the mapping to chipset ports remains unresolved.
- `SILICON-DATASHEET`: [Broadcom BCM53125 product page](https://www.broadcom.com/products/ethernet-connectivity/switching/roboswitch/bcm53125) and [BCM53125 product brief](https://www.mouser.com/datasheet/2/678/broadcom_limited_avgo_s_a0006777419_1-1747564.pdf). These establish silicon interface capabilities, not this board's selected mode or delays.
- `UPSTREAM`: OpenWrt pinned [`bcm63268.dtsi`](https://github.com/openwrt/openwrt/blob/5edcc1c43cb97048b506168fbbe00538956796d6/target/linux/bmips/dts/bcm63268.dtsi), [Comtrend VG-8050 DTS](https://github.com/openwrt/openwrt/blob/5edcc1c43cb97048b506168fbbe00538956796d6/target/linux/bmips/dts/bcm63169-comtrend-vg-8050.dts), and [Sagem F@ST 3864 OP DTS](https://github.com/openwrt/openwrt/blob/5edcc1c43cb97048b506168fbbe00538956796d6/target/linux/bmips/dts/bcm63168-sagem-fast-3864-op.dts). The latter two are comparison-only; none of their SBG topology values are assumed.
- `UPSTREAM`, Linux stable `v6.18.54`, peeled commit `1b357ecb321392158d507b04672ffee57bfa071d`: [B53 chip profile](https://github.com/torvalds/linux/blob/1b357ecb321392158d507b04672ffee57bfa071d/drivers/net/dsa/b53/b53_common.c), [B53 SPI match](https://github.com/torvalds/linux/blob/1b357ecb321392158d507b04672ffee57bfa071d/drivers/net/dsa/b53/b53_spi.c), [B53 MDIO match](https://github.com/torvalds/linux/blob/1b357ecb321392158d507b04672ffee57bfa071d/drivers/net/dsa/b53/b53_mdio.c), [Broadcom DSA tag format](https://github.com/torvalds/linux/blob/1b357ecb321392158d507b04672ffee57bfa071d/net/dsa/tag_brcm.c), and [BCM63xx HSSPI driver](https://github.com/torvalds/linux/blob/1b357ecb321392158d507b04672ffee57bfa071d/drivers/spi/spi-bcm63xx-hsspi.c). OpenWrt DTS/Kconfig source references use OpenWrt commit `5edcc1c43cb97048b506168fbbe00538956796d6`.
- Official-source route: Zyxel describes GPL source request/access through its [Open Source Code portal](https://support.zyxel.eu/hc/en-us/articles/360017067100-Zyxel-Open-Source-Code-MyZyxelPortal-How-to-Access-Zyxel-Open-Source-Code-for-Programmers-GPL). No exact public official SBG3300 archive was located in this pass. Vendor source remains outside public Git.

## Safety and outcome

Read-only stock SSH was used and the owner moved the LAN 1 cable to LAN 2 and
back for the authorized A/B/A test. No register/MMIO selector was used and no
router configuration changed. No raw NAND/MTD, UART, module load, reset,
reboot, firmware operation, or final image build occurred.
The main board DTS keeps Ethernet, switch, MDIO, and NAND disabled. The
candidate DTS exists only as an offline evidence fixture.

**Outcome: `ETHERNET TOPOLOGY PARTIAL — SPECIFIC HARDWARE VALIDATION REQUIRED`.**
The SoC port map, active family source HSSPI selection, BCM53125 identity,
stock VLAN-1 group, likely 6↔8 cascade, and LAN 1/LAN 2 to stock `eth0`/`eth1`
mapping are source-backed or directly observed as labeled above. LAN 2's
external PHY index, LAN 3/LAN 4/WAN mapping, RGMII timing/reset, final
VLAN/WAN state, tag-format compatibility, and Linux 6.18 DSA runtime remain
blockers.
