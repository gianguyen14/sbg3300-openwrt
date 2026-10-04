# SBG3300 DTS syntax build

Status: `PASS` for standalone DTS parsing and DTB round-trip only. This does
not establish kernel boot, hardware behavior, or flash safety.

## Inputs and toolchain

- Candidate: `dts/bcm63168-zyxel-sbg3300-n000.dts`
- SoC include: pinned OpenWrt `target/linux/bmips/dts/bcm63268.dtsi`
- DTC source: device-tree-compiler upstream checkout, commit
  `7a1e017926004ecff5fce62d62d42ce9f3e00082`
- Linux binding headers: upstream Linux v6.18; vendor bmips interrupt binding
  from the pinned OpenWrt checkout
- DTS SHA256: `b97ff3c63ac8b9bdf1a1d17d431a6bd455b3bc8b18c6ed8d7e0738b8784852ac`
- DTB SHA256: `5089bf72d74aaaf5e6d7a30be1f1cf1fff43a136de5722f95b47253781fd1d21`

## Result

Preprocessing, DTC compile, and DTB-to-DTS round-trip succeeded. DTC emitted
one inherited warning from `bcm63268.dtsi:533`: the upstream SoC switch node
has `#address-cells/#size-cells` without `ranges` or a child `reg` property.
No warning pointed to a SBG3300-specific node.

`fdtget` confirms:

- compatible: `zyxel,sbg3300-n000`, `brcm,bcm63168`, `brcm,bcm63268`
- model: `Zyxel SBG3300-N000 (research-only skeleton)`
- `nflash`: enabled
- NAND ECC step size: 512
- NAND ECC strength: 15

The full build artifact is retained locally at
`builds/dts/bcm63168-zyxel-sbg3300-n000.dtb`; build outputs are intentionally
not tracked in Git. The candidate defines no fixed NAND partitions, Ethernet
ports, switch topology, GPIOs, LEDs, buttons, or MAC offsets.

## Next gate

The isolated OpenWrt device profile still needs an actual target kernel/image
build. The unmodified bmips baseline build is compiling toolchain dependencies.
No factory or sysupgrade image is defined for the SBG3300 profile.
