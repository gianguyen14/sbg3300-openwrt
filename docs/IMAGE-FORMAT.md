# Stock firmware container notes

The canonical image is a Broadcom/MSTC tag-v6 container. Existing project
offline disassembly and live validator reports in the stock-mod workspace
record a `0x20000` tag/payload prefix, chip ID `63268`, board ID
`963168MXH_17A`, model tag `4506`, payload CRC32, header CRC32, and a trailer
whose CRC is checked when tag byte `0xce` is 1. No cryptographic signature was
identified in that earlier static validator analysis. These notes describe the
stock validation path only; they do not establish that an OpenWrt image can be
wrapped safely or that CRC is a signature.

For the canonical stock file (SHA256
`3b994309aec554c858d8129c17ff1966b11ec33cb9f3e77914bcf211f0310b79`), the
read-only local parser reports:

- image size: 23,876,705 bytes;
- tag v6, identity `MSTC`, model `4506`, chip `63268`, board
  `963168MXH_17A`;
- CFE length 0, rootfs length 23,724,032, kernel length 0;
- payload at file range `[0x20000, 0x16c0000)`;
- header, payload, and trailer CRC checks pass;
- trailer begins at `0x16c0000`.

Reproduce with:

```sh
tools/sbg3300-image-info /path/to/V1.01\(AADY.9\)C0.bin
python3 -m unittest discover -s tests -p 'test_*.py'
```

`tools/sbg3300-image-info` is a read-only offline parser. It does not invoke
the router's validator, write images, create wrappers, or make an image
flashable. Stock-web validator acceptance is a separate gate.
