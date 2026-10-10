# SBG3300 Ethernet and switch topology research

Date: 2026-10-10. Scope: offline source review plus previously authorized,
read-only stock observations. Target: BCM63168D0, board ID
`963168MXH_17A`. OpenWrt baseline `5edcc1c43cb97048b506168fbbe00538956796d6`
(Linux 6.18.54, `bmips/bcm63268`). No router command was run for this report;
the current live evidence is in `LIVE-READONLY-2026-10-10.md`. DSL remains
deferred.

## Finding

**The external switch silicon is verified as BCM53125 for a bootlog that
reports the same board ID, `963168MXH_17A`, as the live stock device.** The
Broadcom bootlog says CFE detected external switch ID 53125, then the Linux
release log says the MDK forces its 53115 driver for that 53125 and initializes
two switch units. This independently closes the switch-identity question.

The complete OpenWrt topology is still unresolved. Exact-family boardparms
describes SoC-side port 6 as RGMII-connected to an external switch and an
external HSSPI switch group on SSB0 with PHY map `0x1e`. It does not identify
the BCM53125 CPU port, RGMII delay settings, electrical interface details,
per-port roles, or jack mapping. The same boardparms entry enables an HSSPI
SSB5 external-chip-select overlay while selecting SSB0 for the external switch;
the source comments also mention SSB5 as an alternate after MDIO resistor
changes. The source does not explain whether the SSB5 overlay is only pinmux
capability for an alternate configuration or serves another board function;
it does not prove that SSB5 actively selects this switch.

The SBG3300 quick-start guide identifies a separate ETHERNET WAN jack beside
ETHERNET 1–4; the user guide calls this the fifth Ethernet port and says it can
be configured as an extra LAN port when DSL is used. Thus a dedicated Ethernet
WAN connector is a verified product fact. The documents do not map it to a
SoC PHY or a BCM53125 port. No port in the active boardparms branch is labelled
WAN, and stock `eth4.1`/PPP layering plus switch indices are not physical-jack
identifiers. SoC port 3/PHY ID 4 is a candidate, not a confirmed ETHWAN
mapping.

## Verified facts and evidence class

| Fact | Evidence and limit |
|---|---|
| Public bootlog board ID is `963168MXH_17A` | `STOCK-BOOT-LOG`: CFE board ID at log line 54; the page is the [public SBG3300 bootlog](https://jirkabalhar.cz/posts/hack-router/zyxel-sbg3300-bootlog.html). |
| Same boot reports external switch ID 53125 | `STOCK-BOOT-LOG`: CFE line 38 says external switch ID 53125. The same log reports BCM63168D0. This is direct silicon identity evidence for the logged unit and exact board ID, not a physical jack map. |
| Booted Linux uses the 4.12L.06B family release and an MDK 53115 driver forced for 53125 | Log lines 402–408 report release `4.12L.06B`, forced 53115 driver, two switch units, unit 0 `phy_pbmp=0x18/config_pbmp=0x58`, and unit 1 `phypbmp=0x1e`. This resolves why a stock 53125 may be initialized through 53115-compatible MDK code; it does not imply Linux `b53` must use that compatibility driver. |
| Live device has the same board ID and SoC | `LIVE-DEVICE`: previous owner-authorized stock SSH report records `963168MXH_17A` and BCM63168D0. No new router access was needed. Public log and live device agree on the board ID; exact PCB artwork/revision marking was not observed. |
| Stock software binds a generic HSSPI child at `spi1.0` | `LIVE-DEVICE`: sysfs modalias/driver `bcm_HSSpiDev0`, previously recorded in the live report. It does not report the chip ID or tell which switch registers are behind that child. |
| Live stock logical interfaces map to switch index values | `LIVE-DEVICE`: boot maps `eth0→4`, `eth2→2`, `eth3→1`, `eth4→11`, `eth5→12`; `eth4.1` appears under PPP. These are stock driver indices, not DSA port numbers or physical jacks. |
| A separate Ethernet WAN connector exists | `PRODUCT-DOCUMENTATION`: SBG3300-N000 quick-start guide labels ETHERNET WAN separately from ETHERNET 1–4; its user guide describes ETHWAN as the fifth Ethernet port and says it can be reconfigured as an extra LAN port. This establishes a connector/role, not its switch index or wiring. |
| Exact-family boardparms has two Ethernet groups | `FAMILY-SOURCE`, local mirror revision `e2f23ddbb20bf75689372b6e6a5a0dc613f6e313`, `boardparms.c:2878–2944`: active `#if 1` branch selects MMAP map `0x58` and HSSPI SSB0 map `0x1e`. Mirror was read-only and remains outside the public repository. |
| The board table combines an SSB0 switch setting with an SSB5 external-CS overlay | `FAMILY-SOURCE`, same entry: selected switch config is `BP_ENET_CONFIG_HS_SPI_SSB_0`; the GPIO overlay includes `BP_OVERLAY_HS_SPI_SSB5_EXT_CS`; adjacent comment describes SSB5 as an alternate after MDIO hardware/resistor changes. Their relationship is not established, and the overlay does not prove active SSB5 selection. |
| Pinned OpenWrt has the needed driver families | `UPSTREAM`: target config selects `CONFIG_BCM6368_ENETSW`, `CONFIG_B53`, `CONFIG_B53_SPI_DRIVER`, and `CONFIG_NET_DSA`; pinned `b53_spi.c` contains the `brcm,bcm53125` match. Availability is source/build evidence only. |

The public blog describes the bootlog as coming from an SBG3300 and the bootlog
itself prints the board ID and switch ID together. It does not state a PCB
silkscreen revision, so “same revision” here means the matching firmware board
ID, not proof of identical board artwork or component population.

## Source trace: two switch units and candidate wiring

Exact-family source references below are to the public mirror at revision
`e2f23ddbb20bf75689372b6e6a5a0dc613f6e313`. Vendor implementation files were
reviewed locally; no vendor source was copied into this repository.

- `shared/opensource/boardparms/bcm963xx/boardparms.c:2878–2944` is the
  `963168MXH_17A` entry. Its compiled `#if 1` branch sets the internal/MMAP
  group `portMap=0x58`: ports 3, 4, and 6. It gives port 3 `BP_PHY_ID_4`, port
  4 `TMII_DIRECT|0x14`, and port 6 `RGMII_DIRECT|EXTSW_CONNECTED`.
- The second/external-switch group is HSSPI SSB0, `portMap=0x1e`, with PHY IDs
  1–4. It is consistent with the live generic `spi1.0` child and with the
  bootlog's unit-1 `phypbmp=0x1e`, but is not a complete Linux chip-select or
  pinmux contract.
- `shared/opensource/include/bcm963xx/boardparms.h:296–301` defines the
  external SSB4/5/6/7 overlays. The SBG entry requests SSB5 external CS in its
  overlay while the active switch config decodes to HSSPI SSB0. This is an
  unresolved coexistence, not proof that both selects are active for this switch.
  The HSSPI
  decoder in `bcmdrivers/opensource/net/enet/shared/bcmswaccess.c:608–641`
  maps an HSSPI config enum to a bus plus SSB index; its following ID-read
  path (`:710–725`) uses that HSSPI bus/index for the switch identity. These
  are family-source contracts, not direct Linux 6.18 hardware behavior.
- `EXTSW_CONNECTED` marks the SoC-side MAC/PHY entry as connected to an
  external switch. It does not encode the far-end switch port number. The
  boardparms entry therefore backs a SoC port 6 ↔ external switch connection,
  but does not by itself prove that the far-end is BCM53125 port 8.
- Stock MDK unit 0 `config_pbmp=0x58` and unit 1 `phypbmp=0x1e` align with the
  exact-family source's two port maps. This is strong cross-checking of the
  two-group interpretation. `phy_pbmp=0x18` is the stock unit-0 PHY bitmap;
  its distinction from `config_pbmp` demonstrates that configured MAC ports
  and scanned PHY ports differ.

Candidate wiring, with uncertainty shown explicitly:

```text
BCM63168D0 integrated switch / Ethernet MAC
  port 3 (PHY_ID_4; role unknown) ------------------------- unknown PHY/jack
  port 4 (TMII_DIRECT | 0x14; direct link role unknown) --- unknown peer
  port 6 (RGMII_DIRECT | EXTSW_CONNECTED) -----------------┐
                                                           │ RGMII candidate;
BCM53125 external switch                                   │ CPU-side port not
  ports 1–4 (boardparms PHY map 0x1e) --------------------- │ proven
  port 8 as CPU/DSA link ----------------------------------┘ sibling-DTS inference
  HSSPI control path: likely bcm6328 HSSPI, alias spi1, SSB0 candidate;
                     overlay also enables external SSB5 CS (purpose unresolved)
```

The port-8 CPU link is plausible, not an SBG3300-verified fact. Both comparison
DTS files use BCM53125 port 8 for their CPU link, but they are different boards
with different attachment buses and different SoC switch ports.

## HSSPI, MDIO, PHY and RGMII

The pinned OpenWrt `bcm63268.dtsi` aliases `spi1` to `&hsspi` and declares the
controller as `brcm,bcm6328-hsspi` at `0x10001000`; it has individual pinctrl
groups including `pinctrl_hsspi_cs5`. The live `spi1.0` observation is
consistent with alias `spi1` and CS index 0. The exact-family boardparms
SSB0 setting is consistent with CS/index 0. The SSB5 external-CS overlay and
alternate-configuration comment are not explained well enough to identify
their relation to the active switch wiring.

The active boardparms external group describes HSSPI, not MDIO. Linux has two
possible B53 access paths relevant here: `b53_spi` supports
`brcm,bcm53125`, while `b53_mdio` is for MDIO-attached B53 devices. The SoC
`bcm6368-enetsw` node owns its own internal MDIO sub-bus; the generic
`mdio_ext` label in `bcm6368.dtsi` is not evidence that the SBG external switch
is wired there. Do not declare a duplicate BCM53125 under `mdio_ext` while also
binding it to HSSPI. Doing so risks two switch instances/PHY scans claiming the
same silicon or bus address.

The exact SBG boardparms entry establishes an RGMII connection on integrated
port 6, but does not specify receive/transmit delay or whether delay is supplied
by either endpoint. `rgmii-id` in comparison DTS files is not transferable
evidence. The 53125 silicon ID and stock MDK compatibility workaround do not
settle Linux DSA CPU-port mode, timing, polarity, fixed-link rate, or switch
reset sequencing.

## Comparison devices only

- Pinned OpenWrt `bcm63169-comtrend-vg-8050.dts` enables HSSPI with CS5
  pinctrl, 781 kHz, CPHA+CPOL, BCM53125 at `switch@5`, DSA member `<1 0>`,
  external port 8 linked to internal `switch0port6` with `rgmii-id`, and a
  labeled port 4 `wan`. This demonstrates one valid driver/bus arrangement;
  it is BCM63169 hardware and does not resolve the SBG's SSB0/SSB5 overlay
  question or prove its WAN port.
- Pinned OpenWrt `bcm63168-sagem-fast-3864-op.dts` attaches a BCM53125 at
  `&mdio_ext`, address `0x1e`; its external port 8 links to internal
  `switch0port4` with `rgmii-id`. This is same-SoC-family comparison only. Its
  MDIO bus, internal port 4, delays, port labels, and switch topology cannot be
  copied to SBG3300.

These siblings also illustrate why address and scan ownership matter:
BCM53125 appears at HSSPI chip-select 5 on one board and MDIO address `0x1e`
on another. The SBG family boardparms says HSSPI SSB0. A driver tree that scans
MDIO and HSSPI for the same external switch without a board-specific ownership
contract can create duplicate probes or collisions.

## WAN, VLAN and physical-port mapping

The physical ETHWAN connector and four ETHERNET 1–4 LAN connectors are
documented. Mapping those five connectors to boardparms ports and stock logical
interfaces is still unresolved.

1. Exact active SBG boardparms says SoC port 3 uses PHY ID 4, but does not
   label it WAN. It is a candidate ETHWAN attachment because the product has
   four LAN jacks plus a fifth Ethernet WAN jack. A comment in another
   Broadcom board entry that labels its own port 3 WAN is only supporting
   analogy, not SBG proof.
2. The external BCM53125's boardparms PHY bitmap covers ports 1–4 and does not
   label any port WAN. Those four ports could plausibly serve the four LAN
   jacks, but that assignment is not proven. VG-8050's port-4 WAN label is
   sibling-only and is not an SBG mapping.
3. Public CFE reports port 4 link up at boot. It does not state which connector
   that means. Live stock `ethN` switch indices likewise do not decode to
   silkscreen jack numbers without the stock switch VLAN/config mapping.
4. Live stock evidence shows `eth4.1` under PPP and link on `eth4` at the
   observation time. It may represent stock WAN service layering; DSL was
   idle, and this does not establish a discrete Ethernet-WAN jack or a DSA
   switch VLAN table. The only observed VLAN subinterface suffix is `.1`; its
   complete ingress/egress membership/tagging rules are unavailable.

Candidate hypotheses to test against non-invasive evidence later:

| Hypothesis | Basis | Status |
|---|---|---|
| BCM53125 port 8 is CPU link to BCM63168 integrated port 6 | Exact SBG boardparms proves integrated port 6 to an external switch; both sibling DTS examples use external port 8 | Plausible; far-end port and timing require board-specific confirmation |
| BCM53125 ports 1–4 serve ETHERNET 1–4 | Four user PHYs in exact boardparms and four LAN jacks in product guide | Plausible count match; jack-to-port mapping unverified |
| SoC integrated port 3 / PHY ID 4 serves ETHWAN | Exact boardparms provides a PHY-backed integrated port 3 and product guide documents a fifth Ethernet WAN connector | Candidate; no source directly ties the jack to port 3 |
| BCM53125 port 4 is Ethernet WAN | VG-8050 comparison DTS uses this role | Sibling-only hypothesis; not supported by SBG mapping |
| `eth4.1` maps to the discrete WAN jack | Stock PPP-over-VLAN observation | Unsupported; no jack/link correlation or full VLAN table |

## Linux 6.18.54 integration assessment

Pinned target configuration already builds `BCM6368_ENETSW`, DSA, B53, and
`B53_SPI_DRIVER`. Existing reviewed `bcm6368-enetsw` lifetime/resource changes
compile against the pinned kernel; the exact artifact and tests remain recorded
in `PRE-FINAL-ENGINEERING.md`. `b53_spi.c` matches `brcm,bcm53125`. No missing
driver implementation is the current blocker.

Required before enabling nodes:

- resolve the active HSSPI chip-select wiring and the purpose of the SSB5
  external-CS overlay, then set controller pinctrl, select, mode, and clock
  from board-specific evidence;
- identify BCM53125 CPU port and the DSA link to the exact internal port;
- verify RGMII delays/clock direction and whether a fixed link is valid;
- determine which internal/external PHY addresses are scanned by each Linux
  MDIO bus and avoid registering the external switch twice;
- acquire the stock port/VLAN mapping and prove physical jack-to-switch-port
  correspondence without writing selectors or changing live config;
- determine MAC provisioning from a supported, non-private source before
  adding `nvmem-cells` or offsets;
- only then author an isolated SBG candidate DTS, run DTC, binding schemas, and
  full target builds. Keep current switch/MDIO and external-switch nodes
  disabled until those facts are resolved.

No switch/MAC/VLAN DTS correction is justified from current evidence. The
existing board disables `switch0` and `mdio`, has no BCM53125 node, and does
not enable HSSPI for the switch. This report does not activate them.

## Tests and build results

- New negative contract case rejects an enabled `brcm,bcm53125` DT node, so a
  verified silicon ID cannot be mistaken for a verified topology.
- Existing Python/native/sanitizer/MIPS test and pinned OpenWrt build results
  are preserved; this research report does not change kernel runtime sources
  or any kernel build inputs.
- The previously reviewed `bcm6368-enetsw` module built as ELF32 MIPS
  big-endian/o32 for Linux 6.18.54, vermagic `6.18.54 SMP mod_unload BMIPS
  32BIT`, SHA256
  `89c26b4d872fb86a9f8839bbbe9f077ce64e5f7f99017d9258ccf1bd54e8f1b2`,
  with zero missing imports. This proves compile/link only.
- B53 SPI compile coverage and its hash are recorded in
  `reports/PRE-FINAL-ACCEPTED-ARTIFACTS.tsv`; it was built in a coverage
  configuration, not activated or built as an SBG3300 runtime configuration.
- Full DTC/schema/build reruns are unnecessary because no DTS or kernel source
  changed. Current main board and test fixture retain all uncertain switch
  nodes disabled. No runtime traffic, link, VLAN, or OpenWrt test is claimed.

## Remaining evidence

1. Board-specific confirmation of HSSPI bus/CS and the purpose of the SSB5
   external-CS overlay.
2. BCM53125 CPU port, port interface mode, clock delay responsibility, and
   reset/strap ownership for `963168MXH_17A`.
3. Stock VLAN table and safe logical-to-physical jack mapping evidence.
4. Which SoC PHY/port carries the documented ETHWAN connector and whether the
   four BCM53125 PHY ports map one-to-one to ETHERNET 1–4.
5. Linux runtime DSA probe, PHY/link, VLAN forwarding, WAN/LAN separation and
   teardown validation under OpenWrt. These require a separately approved,
   non-destructive device test; no such test is performed here.

## Source links

- Public [SBG3300 bootlog](https://jirkabalhar.cz/posts/hack-router/zyxel-sbg3300-bootlog.html).
- Zyxel's [SBG3300 multi-WAN announcement](https://www.zyxel.com/service-provider/na/en/news/event/zyxel-launches-business-class-vdsl2-gateway-3g-4g-lte-backup-mobile-world-congress) lists VDSL2, Gigabit Ethernet, and USB mobile WAN. The SBG3300-N000 [quick-start guide](https://manualzz.com/doc/70973145/zyxel-communications-sbg3300-n000-quick-start-manual) labels the ETHERNET WAN jack separately from ETHERNET 1–4; the [user guide's fifth-Ethernet-port page](https://www.manualslib.com/manual/597946/Zyxel-Communications-Sbg3300-N000.html?page=195) says ETHWAN can be configured as an extra LAN port.
- Broadcom family [boardparms entry](https://github.com/nomis/bcm963xx_4.12L.06B_consumer/blob/e2f23ddbb20bf75689372b6e6a5a0dc613f6e313/shared/opensource/boardparms/bcm963xx/boardparms.c#L2878-L2944), [boardparms definitions](https://github.com/nomis/bcm963xx_4.12L.06B_consumer/blob/e2f23ddbb20bf75689372b6e6a5a0dc613f6e313/shared/opensource/include/bcm963xx/boardparms.h#L296-L301), and [HSSPI switch bus/ID path](https://github.com/nomis/bcm963xx_4.12L.06B_consumer/blob/e2f23ddbb20bf75689372b6e6a5a0dc613f6e313/bcmdrivers/opensource/net/enet/shared/bcmswaccess.c#L608-L725).
- Pinned OpenWrt [`bcm63268.dtsi`](https://github.com/openwrt/openwrt/blob/5edcc1c43cb97048b506168fbbe00538956796d6/target/linux/bmips/dts/bcm63268.dtsi#L25-L25), [Comtrend VG-8050 DTS](https://github.com/openwrt/openwrt/blob/5edcc1c43cb97048b506168fbbe00538956796d6/target/linux/bmips/dts/bcm63169-comtrend-vg-8050.dts#L47-L100), [Sagem F@ST 3864 OP DTS](https://github.com/openwrt/openwrt/blob/5edcc1c43cb97048b506168fbbe00538956796d6/target/linux/bmips/dts/bcm63168-sagem-fast-3864-op.dts#L157-L201), and [`b53_spi.c`](https://github.com/openwrt/openwrt/blob/5edcc1c43cb97048b506168fbbe00538956796d6/target/linux/generic/files/drivers/net/phy/b53/b53_spi.c#L320-L320).

**Result: `ETHERNET TOPOLOGY PARTIAL — HARDWARE EVIDENCE REQUIRED`.** External
switch identity and the two-unit board configuration are verified; WAN/LAN
topology and runtime operation remain unresolved.
