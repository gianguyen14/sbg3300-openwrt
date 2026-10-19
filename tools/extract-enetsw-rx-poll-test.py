#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Extract real enetsw callbacks from the supplied prepared Linux source."""
import argparse
from pathlib import Path


def extract(source):
    start = source.index('struct bcm6368_enetsw_desc {')
    end = source.index('\nstruct bcm6368_enetsw {', start)
    pieces = [source[start:end]]
    for name in ('receive_queue', 'tx_reclaim', 'poll'):
        start = source.index('static int bcm6368_enetsw_' + name + '(')
        end = source.index('\n}', start) + 2
        pieces.append(source[start:end])
    return '\n\n'.join(pieces) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    args.output.write_text(extract(args.source.read_text()))


if __name__ == '__main__':
    main()
