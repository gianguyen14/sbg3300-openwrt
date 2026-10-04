# Hardware evidence

## Direct observations from the live stock-custom router

Read-only snapshot collected 2026-10-04 via the established `sbg3300` wrapper.
No configuration or flash writes were made.

| Component | Observation | Confidence |
|---|---|---|
| Board | `963168MXH_17A` | Direct `/proc/cpuinfo` |
| SoC | BCM63168D0, chipId `0x631680D0` | Direct dmesg |
| CPU | Two Broadcom4350 V8.0 cores, ~400 BogoMIPS each | Direct `/proc/cpuinfo` |
| RAM | 128 MiB physical; kernel MemTotal 123392 KiB | Direct boot log + `/proc/meminfo` |
| Kernel | Linux 2.6.30, SMP, PREEMPT, vendor build date 2018-05-24 | Direct `uname` |
| NAND | 128 MiB; 2048-byte writesize; 64-byte OOB; ECC step 512, strength 15; on-flash BBT | Direct dmesg |
| USB | Broadcom PCI function 14e4:6300 enumerates EHCI and OHCI | Direct sysfs/boot log |
| WLAN | PCI function 14e4:435f; proprietary stock `wl` reports BCM435f and loads map/NVRAM files | Direct sysfs + dmesg |
| DSL | BCM63168D0 ADSL/XTM stack; ATM/PTM non-bonding; `adsldd`, `bcmxtmcfg`, `bcm_enet`, FAP/BPM modules | Direct boot log/module list |
| WAN path | `ppp2.1 -> eth4.1 -> eth4`; `eth4.1 -> eth4` is explicitly logged | Direct vendor boot log |
| Ethernet board wiring | Exact board-ID table in a BCM63168D0 4.12L.06B source mirror defines two PHY groups, one external switch on HS-SPI SSB0, and a separate memory-mapped group | Matching source entry; source-to-2018-build equivalence remains |
| External switch chip | BCM53125 likely, not directly read from live switch ID | Exact board table says external SPI switch; chip ID remains unproven |
| AFE | Source table gives internal 6302 Annex A rev 7.2.30 and external 6306/6302 Annex A rev 7.2.21 options | Matching source entry; active variant needs runtime/config cross-check |
| Board LEDs/buttons | Source table provides DSL/VDSL and serial LED pins plus reset/SES external interrupts | Board-ID-matched source; no reset handler will be enabled before GPIO/polarity validation |

No MAC address, serial, PPP identity, secret, or calibration contents are stored
in this report.

## DTS policy

SoC-level nodes may be inherited from upstream `bcm63268.dtsi`. Board-level GPIO,
LED, reset, switch CPU port, PHY addresses, and MAC offsets remain undefined until
confirmed from exact SBG3300 board parameters or equivalent direct evidence.
Reference-board values must not be copied as if they belonged to SBG3300.

## Related upstream devices

The current upstream bmips tree contains BCM63168 support for Actiontec T1200H
and Sagemcom F@ST 3864 OP. F@ST 3864 OP has a BCM53125 DSA topology in its DTS;
that is a comparison lead only. SBG3300 GPIOs and switch wiring may differ.

## Device comparison

| Feature | SBG3300-N000 | Actiontec T1200H | Sagemcom F@ST 3864 OP |
|---|---|---|---|
| SoC | BCM63168D0, live chip ID `0x631680D0` | BCM63168 / bcm63268 family in upstream DTS | BCM63168 / bcm63268 family in upstream DTS |
| RAM | 128 MiB boot report; 123392 KiB Linux total | Board capacity not inferred here | Board capacity not inferred here |
| NAND | 128 MiB, 2 KiB page, 64 B OOB, 128 KiB erase, ECC 15/512, on-flash BBT (live) | DTS: ECC 15/512, BBT, 2 KiB page, 128 KiB block | DTS: ECC 15/512, BBT, 2 KiB page, 128 KiB block |
| NAND layout | Live MTD offsets plus source-derived dual-slot model; unresolved exact writer translation | CFE/WFI-oriented upstream partition model | CFE/WFI plus 4 MiB stock data and 1 MiB hidden tail in upstream DTS |
| External switch | Board table: external switch on HS-SPI SSB0; exact chip ID/ports unproven | Upstream DTS describes BCM53125 DSA | Upstream DTS describes BCM53125 DSA |
| Ethernet | Stock `eth3`/`eth4`; labels and CPU port unresolved | DSA topology is device-specific | DSA topology is device-specific |
| USB | Broadcom PCI 14e4:6300 EHCI + OHCI live | Upstream DTS enables EHCI/OHCI | Upstream DTS enables EHCI/OHCI |
| Wi-Fi | PCI 14e4:435f, stock proprietary `wl`; calibration map unknown | Device-specific | Device-specific |
| DSL | BCM63168D0, proprietary ADSL/XTM modules, ATM/PTM observed | Not treated as upstream DSL support | Not treated as upstream DSL support |
| PCIe | Broadcom bridge 14e4:6326 and WLAN enumerate live | Upstream board definition | Upstream board definition |

Reference data comes from the pinned OpenWrt DTS files in
`source/openwrt/target/linux/bmips/dts/`. It is comparison evidence only; no
GPIO, port order, partition writer behavior, or DSL configuration is inherited
without SBG3300-specific proof.
