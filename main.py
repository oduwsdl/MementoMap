#!/usr/bin/env python3

import argparse

from mementomap.mementomap import compact, lookup


def show_lookup(**kw):
    res = lookup(**kw)
    if res:
        print(" ".join(res))


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
    parser_compact.set_defaults(func=compact)

    parser_lookup = subparsers.add_parser("lookup", help="Look for a SURT into a MementoMap")
    parser_lookup.add_argument("mmap", help="MementoMap file to look into")
    parser_lookup.add_argument("surt", help="SURT to look for")
    parser_lookup.set_defaults(func=show_lookup)

    args = parser.parse_args()
    try:
        args.func(**vars(args))
    except Exception as e:
        parser.print_help()
