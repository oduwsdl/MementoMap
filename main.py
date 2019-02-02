#!/usr/bin/env python3

import sys
import argparse

from mementomap.mementomap import compact, lookup


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_compact = subparsers.add_parser("compact", help="Compact a large MementoMap file into a small one")
    parser_compact.add_argument("infile", help="Input MementoMap file")
    parser_compact.add_argument("outfile", help="Output MementoMap file")
    parser_compact.add_argument("--hcf", type=float, metavar="", default=1.0, help="Host compaction factor")
    parser_compact.add_argument("--pcf", type=float, metavar="", default=1.0, help="Path compaction factor")
    parser_compact.add_argument("--ha", type=float, metavar="", default=16.329, help="Power law alpha parameter for host")
    parser_compact.add_argument("--pa", type=float, metavar="", default=24.546, help="Power law alpha parameter for path")
    parser_compact.add_argument("--hk", type=float, metavar="", default=0.714, help="Power law k parameter for host")
    parser_compact.add_argument("--pk", type=float, metavar="", default=1.429, help="Power law k parameter for path")
    parser_compact.add_argument("--hdepth", type=int, metavar="", default=8, help="Max host depth")
    parser_compact.add_argument("--pdepth", type=int, metavar="", default=9, help="Max path depth")

    parser_lookup = subparsers.add_parser("lookup", help="Look for a SURT into a MementoMap")
    parser_lookup.add_argument("mmap", help="MementoMap file to look into")
    parser_lookup.add_argument("surt", help="SURT to look for")

    args = parser.parse_args()

    def print_help():
        print(f"Usage:\n  {sys.argv[0]} lookup <infile:path> <key:surt>\n  {sys.argv[0]} compact <infile:path> <outfile:path> <hcf:float> <pcf:float>", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) < 2 or (sys.argv[1] == "compact" and len(sys.argv) < 6) or (sys.argv[1] == "lookup" and len(sys.argv) < 4):
        print_help()

    if sys.argv[1] == "compact":
        compact(sys.argv[2], sys.argv[3], hcf=float(sys.argv[4]), pcf=float(sys.argv[5]))
    elif sys.argv[1] == "lookup":
        res = lookup(sys.argv[2], sys.argv[3])
        if res:
            print(" ".join(res))
