#!/usr/bin/env python3
"""Full JFFS2 rootfs extractor for BCM 4.12L big-endian (SBG3300 stock payload).

CRC convention (empirically verified against stock): crc32_le(seed=0, data)
with NO final xor; hdr_crc over first 8 bytes; dirent node_crc over first 32;
inode node_crc over first 60; data/name crc over payload bytes.
Offline, read-only. Usage: jffs2_extract.py <stock.bin> <outdir>
"""
import struct, sys, zlib
from pathlib import Path

NODETYPE_DIRENT = 0xE001
NODETYPE_INODE = 0xE002
INODE_HDR = 68
DIRENT_HDR = 40
BE = '>'

def crc_le(data):
    c = 0
    for b in data:
        c ^= b
        for _ in range(8):
            c = (c >> 1) ^ (0xEDB88320 if c & 1 else 0)
    return c & 0xffffffff

def walk(payload):
    n = len(payload)
    off = 0
    while off + 12 <= n:
        if payload[off:off+2] == b'\x19\x85':
            magic, ntype, totlen, hcrc = struct.unpack_from(BE+'HHII', payload, off)
            if totlen < 12 or off + totlen > n:
                off += 2; continue
            if crc_le(payload[off:off+8]) != hcrc:
                off += 2; continue
            yield ntype, off, totlen
            off += (totlen + 3) & ~3
        else:
            off += 2

def main():
    src, outdir = sys.argv[1], sys.argv[2]
    blob = Path(src).read_bytes()
    payload = blob[0x20000:0x16c0000]
    print(f"payload: {len(payload)} bytes")

    inodes = {}
    dirents = {}
    sizes = {}
    n_inode = n_dirent = 0
    for ntype, off, totlen in walk(payload):
        if ntype == NODETYPE_INODE and totlen >= INODE_HDR:
            d = payload[off:off+totlen]
            ino, version, mode = struct.unpack_from(BE+'III', d, 12)
            isize, atime, mtime, ctime, foff = struct.unpack_from(BE+'IIIII', d, 28)
            csize, dsize = struct.unpack_from(BE+'II', d, 48)
            compr, usercompr, flags = struct.unpack_from(BE+'BBH', d, 56)
            data_crc, node_crc = struct.unpack_from(BE+'II', d, 60)
            if crc_le(d[:60]) != node_crc:
                continue
            if totlen < INODE_HDR + csize:
                continue
            frags = inodes.setdefault(ino, {})
            frags[foff] = (version, csize, dsize, compr, off + INODE_HDR, data_crc)
            cur = sizes.get(ino)
            if cur is None or version >= cur[0]:
                sizes[ino] = (version, isize)
            n_inode += 1
        elif ntype == NODETYPE_DIRENT and totlen >= DIRENT_HDR:
            d = payload[off:off+totlen]
            pino, version, child, mctime = struct.unpack_from(BE+'IIII', d, 12)
            nsize, dtype, unused = struct.unpack_from(BE+'BBH', d, 28)
            node_crc, name_crc = struct.unpack_from(BE+'II', d, 32)
            if crc_le(d[:32]) != node_crc:
                continue
            if totlen < DIRENT_HDR + nsize:
                continue
            name = d[DIRENT_HDR:DIRENT_HDR+nsize].decode('utf-8', 'replace')
            if crc_le(name.encode('utf-8')) != name_crc:
                continue
            tbl = dirents.setdefault(pino, {})
            if child == 0:
                tbl.pop(name, None)
            else:
                cur = tbl.get(name)
                if cur is None or version >= cur[1]:
                    tbl[name] = (child, version, dtype)
            n_dirent += 1
    print(f"inode records: {n_inode}, dirent records: {n_dirent}, inos: {len(inodes)}")

    def decompress(compr, data, dsize):
        if compr == 0:
            return data
        if compr == 6:
            try:
                return zlib.decompress(data)
            except Exception:
                return None
        if compr == 1:
            return b'\x00' * dsize
        if compr == 4:
            return data
        return None

    def read_file(ino):
        frags = inodes.get(ino, {})
        if not frags:
            return None
        _, isize = sizes.get(ino, (0, 0))
        buf = bytearray(isize)
        for foff, (version, csize, dsize, compr, doff, data_crc) in frags.items():
            raw = payload[doff:doff+csize]
            if crc_le(raw) != data_crc:
                continue
            out = decompress(compr, raw, dsize)
            if out is None:
                continue
            end = min(foff + len(out), isize)
            buf[foff:end] = out[:end-foff]
        return bytes(buf)

    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    seen = set()
    queue = [(1, out)]
    n_files = 0
    while queue:
        ino, dirpath = queue.pop(0)
        if ino in seen:
            continue
        seen.add(ino)
        for name, (child, version, dtype) in dirents.get(ino, {}).items():
            safe = name.replace('/', '_').replace('\x00', '')
            if not safe:
                continue
            childpath = dirpath / safe
            if dtype == 2 or (dtype == 4 and child in inodes):
                childpath.mkdir(parents=True, exist_ok=True)
                queue.append((child, childpath))
            else:
                data = read_file(child)
                if data is not None:
                    childpath.write_bytes(data)
                    n_files += 1
    print(f"files extracted: {n_files} -> {outdir}")

if __name__ == '__main__':
    main()