# Remote/off-device work

A contributor does not need an SBG3300 to continue source research, builds,
patching, and static analysis. A Linux x86_64 machine with Git, internet access,
OpenWrt build dependencies, ample disk, and preferably 8+ GiB RAM is suitable.
OpenWrt rejects checkout paths containing spaces; choose a space-free
`OPENWRT_DIR`.

Read [AGENTS.md](../AGENTS.md), [STATUS.md](../STATUS.md),
[HANDOFF-HERMES.md](../HANDOFF-HERMES.md), then [REPRODUCE.md](../REPRODUCE.md).
The scripts fetch only pinned public OpenWrt source. Vendor source and blobs
require separate provenance and license review; they are not auto-fetched.

Fedora example build dependencies (names can change by Fedora release):

```sh
sudo dnf install @development-tools @c-development git gcc g++ \
  ncurses-devel zlib-devel openssl-devel perl perl-FindBin perl-Thread-Queue \
  python3 python3-distutils-extra rsync unzip bzip2 gawk gettext which \
  file wget curl patch diffutils perl-Data-Dumper perl-ExtUtils-MakeMaker
```

Use the current OpenWrt build prerequisites for other distributions. Do not
install random binary toolchains or vendor blobs into the project. The build
can take substantial time and disk. Generated checkout/build trees are ignored
and remain local.

Offline-capable tasks include porting the public XTM code, investigating
boardparms/switch mappings, image-format analysis from public source and
sanitized evidence, Wi-Fi bus discovery research, compile probes, tests, and
documentation. OpenWrt boot, switch topology/link mapping, Wi-Fi association,
DSL sync, PPPoE, performance, and recovery remain `NEEDS-DEVICE`.
