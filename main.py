#!/usr/bin/env python3

import argparse
import gzip
import sys

from mementomap.mementomap import compact, lookup


def run_compact(**kw):
    if kw["infile"].endswith(".gz"):
        fobj = gzip.open(kw["infile"], "rb")
    elif kw["infile"] == "-":
        fobj = sys.stdin.buffer
    else:
        fobj = open(kw["infile"], "rb")
    kw["infiter"] = fobj
    try:
        res = compact(**kw)
    except Exception as e:
        print(e)
    fobj.close()
    print(f'{res["inlines"]} {res["outlines"]} {res["inbytes"]} {res["outbytes"]}')


def run_lookup(**kw):
    res = lookup(**kw)
    if res:
        print(" ".join(res))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    compact_parser = subparsers.add_parser("compact", help="Compact a large MementoMap file into a small one")
    compact_parser.add_argument("infile", help="Input MementoMap file")
    compact_parser.add_argument("outfile", help="Output MementoMap file")
    compact_parser.add_argument("--hcf", type=float, metavar="", default=1.0, help="Host compaction factor")
    compact_parser.add_argument("--pcf", type=float, metavar="", default=1.0, help="Path compaction factor")
    compact_parser.add_argument("--ha", type=float, metavar="", default=16.329, help="Power law alpha parameter for host")
    compact_parser.add_argument("--pa", type=float, metavar="", default=24.546, help="Power law alpha parameter for path")
    compact_parser.add_argument("--hk", type=float, metavar="", default=0.714, help="Power law k parameter for host")
    compact_parser.add_argument("--pk", type=float, metavar="", default=1.429, help="Power law k parameter for path")
    compact_parser.add_argument("--hdepth", type=int, metavar="", default=8, help="Max host depth")
    compact_parser.add_argument("--pdepth", type=int, metavar="", default=9, help="Max path depth")
    compact_parser.set_defaults(func=run_compact)

    lookup_parser = subparsers.add_parser("lookup", help="Look for a SURT into a MementoMap")
    lookup_parser.add_argument("mmap", help="MementoMap file to look into")
    lookup_parser.add_argument("surt", help="SURT to look for")
    lookup_parser.set_defaults(func=run_lookup)

    args = parser.parse_args()
    try:
        args.func(**vars(args))
    except Exception as e:
        parser.print_help()
