# Live stock boot and hardware observations

Read-only collection on 2026-10-04 through the existing wrapper. No flash or
configuration operation was issued. Device-specific MAC addresses and other
unique values were omitted.

- SoC ID: `0x631680D0` (BCM63168D0 family).
- Board string: `963168MXH_17A`.
- CPUs: two Broadcom4350 V8.0 cores; stock kernel 2.6.30 SMP/PREEMPT.
- Memory: 128 MiB physical; 123392 KiB reported MemTotal.
- NAND: controller v4, 128 MiB; writesize 2048, OOB 64, ECC 512-byte step,
  strength 15, BBT enabled.
- Follow-up read-only `dmesg | grep -Ei 'nand|onfi|spansion|flash'` on
  2026-10-04 confirmed the BBT/controller messages and MTD registrations but
  did not expose a JEDEC part ID. The Spansion S34ML01G1 identifier comes from
  the supplied hardware inventory and is not asserted as live ID evidence.
- USB: PCI 14e4:6300 exposes EHCI and OHCI host controllers.
- WLAN: PCI 14e4:435f; stock proprietary `wl` reports BCM435f, driver
  `6.30.102.7.cpe4.12L06B.1`.
- DSL/XTM: proprietary `adsldd` and `bcmxtmcfg`; log reports ATM/PTM
  non-bonding and BCM63168D0. Existing WAN stack is
  `ppp2.1 -> eth4.1 -> eth4`.
- Ethernet: stock `bcm_enet`; logs identify eth3 and eth4 with switch-port
  indices. No complete physical port mapping recovered yet.
- A further read-only scan of `dmesg` and `/proc/bus/pci/devices` found no
  `bcm53125`/`b53` identification. It again showed link events for switch
  indices 1, 11 and 12. PCI functions were WLAN 14e4:435f, USB 14e4:6300
  OHCI/EHCI and bridge 14e4:6326; this PCI scan cannot identify an SPI switch.
- Acceleration: `bcmfap`, `bcm_bpm`, `bcm_ingqos` active; FAP 0 and 1 initialize.
- PCI functions also include Broadcom bridge function 14e4:6326.

The output of the live PCI/dmesg inspection is not copied verbatim because the
stock log includes a device MAC address. This report records only non-unique
hardware identifiers and topology evidence.
