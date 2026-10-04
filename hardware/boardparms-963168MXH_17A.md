# Board-parameter recovery: 963168MXH_17A

## Source provenance and confidence

The public Broadcom 4.12L.06B source mirror contains an exact board ID entry at
`shared/opensource/boardparms/bcm963xx/boardparms.c`, `g_bcm963168mxh_17a`
(around lines 2878-2995). The live router reports the same board ID. This makes
the table highly relevant, but the mirror is dated 2015 and the live vendor
kernel was built in 2018. Runtime and binary cross-checks are still required
before treating every conditional board property as final.

## Direct table facts

- Overlay: PHY, serial LEDs, USB LED, PCIe CLKREQ, HS-SPI SSB5 external-CS GPIO
  muxing.
- LEDs: DSL GPIO14 active-low; secondary DSL GPIO9 active-low; VDSL GPIO15/16
  active-low; SES/WPS serial GPIO7 active-high; WAN data serial GPIO8
  active-low; Internet data GPIO22 active-high; WAN error serial GPIO2
  active-low; power-on GPIO20 active-low; power-stop GPIO21 active-low; USB
  serial GPIO6 active-low.
- Buttons: reset-to-default external interrupt 0; SES/wireless external
  interrupt 1. The table does not by itself provide safe Linux GPIO polarity,
  hold timing, or reset semantics. Do not enable a reset key handler yet.
- AFE: AFE ID0 is internal 6302/Annex A/revision 7.2.30; AFE ID1 is external
  6306 with 6302 line driver/Annex A/revision 7.2.21. AFE reset is GPIO17
  active-low; LD relay is GPIO39 active-high.
- Ethernet table has two external-switch groups. In the `#if 1` branch, the
  first is memory-mapped with port map `0x58`, and the second uses
  `BP_ENET_CONFIG_HS_SPI_SSB_0` with port map `0x1e` and PHY IDs 0 through 3.
  The first group includes direct TMII/RGMII connections. This supports an
  external SPI switch architecture, but does not identify live silicon or map
  chassis labels/DSA CPU port.
- `g_BoardParms` includes this exact array in the 4.12L.06B mirror.

## DTS use policy

The source values can guide a draft after `bp_*` macro decoding. LEDs are lower
risk but still need polarity/function checks. Buttons, especially reset, remain
disabled until the external interrupt and exact physical behavior are matched.
No MAC values or calibration data are carried from device storage into DTS.
