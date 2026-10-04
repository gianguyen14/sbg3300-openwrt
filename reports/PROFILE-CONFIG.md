# SBG3300 profile Kconfig check

Date: 2026-10-04
OpenWrt revision: `5edcc1c43cb97048b506168fbbe00538956796d6`
Port worktree revision: `39daa4cd479b74d0691e681c07a1713dcb1c36a3`

The candidate profile symbol resolves after upstream `make defconfig`:

```text
CONFIG_TARGET_bmips=y
CONFIG_TARGET_bmips_bcm63268=y
CONFIG_TARGET_bmips_bcm63268_DEVICE_zyxel_sbg3300-n000=y
CONFIG_TARGET_INITRAMFS_COMPRESSION_NONE=y
CONFIG_TARGET_ROOTFS_INITRAMFS=y
```

The generated minimal configuration is in `configs/sbg3300_port_defconfig`.
SHA256 of that diffconfig: `78ba206848f434d594ab50f2e8bd8223890d2437b4eadf9542aa2ba46dea4ebe`.

This validates target/profile selection only. It does not compile the board,
prove the initramfs boots, or define any writable image. The profile Makefile
continues to emit only an `-OFFLINE-ONLY.elf` kernel/initramfs artifact and
does not define CFE/factory or sysupgrade outputs.
