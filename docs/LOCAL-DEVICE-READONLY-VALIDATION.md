# Read-Only Device Validation

## Authorized observation recorded 2026-10-10

The owner subsequently authorized existing SSH for non-destructive read-only
diagnostics. The results and safety boundary are recorded in
[../reports/LIVE-READONLY-2026-10-10.md](../reports/LIVE-READONLY-2026-10-10.md).
The pending table below is the original handoff plan, not current authorization
status. This authorization covers stock observations only; it does not authorize
module loading, firmware/image execution, device configuration or flash actions.

## Original handoff plan — authorization was pending

Nothing in this document authorizes running commands on the router. No device was accessed in this handoff. Obtain separate, explicit authorization before any device connection or command execution. Use only the device's already enabled, supported management interface; no UART/serial console, raw MTD, bootloader/CFE, NVRAM, calibration, settings changes, reset/reboot, firmware upload/flash, or experimental module loading.

The following are proposed read-only checks only. Confirm each command is supported by the device's existing shell and ensure output does not include credentials, serials, MAC addresses or private configuration before transferring logs.

Possible commands, if a separately authorized read-only shell exists:

```sh
uname -a
cat /proc/cpuinfo
cat /proc/version
cat /proc/cmdline
cat /proc/modules
cat /proc/interrupts
cat /proc/net/dev
ip -details link show
ip -s link show
cat /proc/bus/pci/devices
lspci -nnk
ls -l /sys/bus/pci/devices
ls -l /sys/bus/spi/devices
ls -l /sys/bus/platform/devices
readlink -f /sys/bus/pci/devices/*/driver
readlink -f /sys/bus/spi/devices/*/driver
readlink -f /sys/bus/platform/devices/*/driver
dmesg --color=never
```

Not every utility or sysfs path will exist on the stock firmware. Do not install utilities or alter the device to make these commands work. Limit dmesg output to relevant driver enumeration and redact sensitive fields before sharing. Do not read `/dev/mtd*`, NVRAM, calibration, credentials, or persistent configuration.

| Check | Authorization | Runtime evidence |
|---|---|---|
| Kernel/SoC/board identity | PENDING AUTHORIZATION | NOT COLLECTED |
| PCI enumeration/driver binding | PENDING AUTHORIZATION | NOT COLLECTED |
| SPI/platform enumeration/driver binding | PENDING AUTHORIZATION | NOT COLLECTED |
| Read-only network link and statistics | PENDING AUTHORIZATION | NOT COLLECTED |
| Read-only dmesg review | PENDING AUTHORIZATION | NOT COLLECTED |

No UART, raw flash operations, settings changes, reset/reboot, firmware operations, or experimental module loading are part of this plan.
