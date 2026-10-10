#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Extract the actual TX callback for CPU-only API-double tests, never runtime."""
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source = (Path(__file__).resolve().parents[1] / "drivers/xtm/xtm_ptm.c").read_text()
    start = source.index("static netdev_tx_t xtm_ptm_xmit(")
    end = source.index("\n/* Retain any ring", start)
    args.output.write_text(source[start:end] + "\n")


if __name__ == "__main__":
    main()
