# Ethernet and switch investigation

The pinned `bmips` target has BCM63168 Ethernet, DSA `b53`, and the `b53_spi`
frontend for `brcm,bcm53125`. The exact-board Broadcom 4.12L.06B boardparms
entry describes an external HSSPI switch group (`SSB_0`, PHY map `0x1e`) and a
separate memory-mapped group (`0x58`). Its selected branch describes integrated
port 4 as `TMII_DIRECT|0x14` and port 6 as
`RGMII_DIRECT|EXTSW_CONNECTED`.

The public SBG3300 bootlog independently identifies BCM53125 on board ID
`963168MXH_17A`, matching the board ID observed in live stock SSH. The Linux
log reports two switch units whose bitmaps align with the two boardparms
groups. See `reports/ETHERNET-SWITCH-TOPOLOGY-RESEARCH.md` for source
references and evidence boundaries.

Live stock sysfs exposes `/sys/devices/platform/bcmhs_spi.1/spi1.0`, bound to
generic `bcm_HSSpiDev0`; it does not expose the switch ID. The board table
selects HSSPI SSB0 but also requests an HSSPI SSB5 external-chip-select overlay
and mentions SSB5 as an alternate after MDIO resistor changes. The controller,
chip-select pinmux, CPU port, RGMII delays, PHY scan ownership, and reset
sequence are therefore not fully resolved.

Comtrend VG-8050 and Sagem F@ST 3864 OP DTS files provide comparison examples
only. They use different switch attachment choices and port wiring. Their
BCM53125 port labels, CPU link, mode, delays, and WAN mapping are not evidence
for the SBG3300.

Stock `ethN` switch indices and `eth4.1`/PPP layering are logical interfaces,
not physical jack labels. No stock VLAN table or safe jack-to-port mapping is
available. Keep switch/MDIO inactive in the SBG3300 DTS; `b53_spi` compile
coverage does not establish an SBG3300 runtime bind or working network.
