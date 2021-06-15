#!/usr/bin/env python3

import argparse
import gzip
import sys
import os

if not __package__:
    sys.path.insert(1, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from mementomap import __VERSION__
from mementomap.cli import compact, generate, lookup


def run_generate(**kw):
    if kw["infile"].endswith(".gz"):
        fobj = gzip.open(kw["infile"], "rb")
    elif kw["infile"] == "-":
        fobj = sys.stdin.buffer
    else:
        fobj = open(kw["infile"], "rb")
    kw["infiter"] = fobj
    res = generate(**kw)
    fobj.close()
    print(f'{res["inlines"]} {res["outlines"]} {res["inbytes"]} {res["outbytes"]} {res["rollups"]}')


def run_compact(**kw):
    if kw["infile"].endswith(".gz"):
        fobj = gzip.open(kw["infile"], "rb")
    elif kw["infile"] == "-":
        fobj = sys.stdin.buffer
    else:
        fobj = open(kw["infile"], "rb")
    kw["infiter"] = fobj
    res = compact(**kw)
    fobj.close()
    print(f'{res["inlines"]} {res["outlines"]} {res["inbytes"]} {res["outbytes"]} {res["rollups"]}')


def run_lookup(**kw):
    mobj = open(kw["mmap"], "rb")
    kw["mmapiter"] = mobj
    res = lookup(**kw)
    mobj.close()
    if res:
        print(f'{res["surtk"]} {res["freq"]} {res["dist"]} {res["surt"]}')


def run_batchlookup(**kw):
    mobj = open(kw["mmap"], "rb")
    kw["mmapiter"] = mobj
    if kw["infile"].endswith(".gz"):
        fobj = gzip.open(kw["infile"], "rb")
    elif kw["infile"] == "-":
        fobj = sys.stdin.buffer
    else:
        fobj = open(kw["infile"], "rb")
    for line in fobj:
        kw["surt"] = line.strip().decode()
        res = lookup(**kw)
        if res:
            print(f'{res["surtk"]} {res["freq"]} {res["dist"]} {res["surt"]}')
    fobj.close()
    mobj.close()


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    generate_parser = subparsers.add_parser("generate", help="Generate a MementoMap from a sorted file with the first columns as SURT (e.g., CDX/CDXJ)")
    generate_parser.add_argument("infile", help="Input SURT/CDX/CDXJ (plain or GZip) file path or '-' for STDIN")
    generate_parser.add_argument("outfile", help="Output MementoMap file path")
    generate_parser.add_argument("--hcf", type=float, metavar="", default=float("inf"), help="Host compaction factor (deafault: Inf)")
    generate_parser.add_argument("--pcf", type=float, metavar="", default=float("inf"), help="Path compaction factor (deafault: Inf)")
    generate_parser.add_argument("--ha", type=float, metavar="", default=16.329, help="Power law alpha parameter for host (default: 16.329)")
    generate_parser.add_argument("--pa", type=float, metavar="", default=24.546, help="Power law alpha parameter for path (default: 24.546)")
    generate_parser.add_argument("--hk", type=float, metavar="", default=0.714, help="Power law k parameter for host (default: 0.714)")
    generate_parser.add_argument("--pk", type=float, metavar="", default=1.429, help="Power law k parameter for path (default: 1.429)")
    generate_parser.add_argument("--hdepth", type=int, metavar="", default=8, help="Max host depth (default: 8)")
    generate_parser.add_argument("--pdepth", type=int, metavar="", default=9, help="Max path depth (default: 9)")
    generate_parser.set_defaults(func=run_generate)

    compact_parser = subparsers.add_parser("compact", help="Compact a large MementoMap file into a small one")
    compact_parser.add_argument("infile", help="Input MementoMap (plain or GZip) file path or '-' for STDIN")
    compact_parser.add_argument("outfile", help="Output MementoMap file path")
    compact_parser.add_argument("--hcf", type=float, metavar="", default=1.0, help="Host compaction factor (deafault: 1.0)")
    compact_parser.add_argument("--pcf", type=float, metavar="", default=1.0, help="Path compaction factor (deafault: 1.0)")
    compact_parser.add_argument("--ha", type=float, metavar="", default=16.329, help="Power law alpha parameter for host (default: 16.329)")
    compact_parser.add_argument("--pa", type=float, metavar="", default=24.546, help="Power law alpha parameter for path (default: 24.546)")
    compact_parser.add_argument("--hk", type=float, metavar="", default=0.714, help="Power law k parameter for host (default: 0.714)")
    compact_parser.add_argument("--pk", type=float, metavar="", default=1.429, help="Power law k parameter for path (default: 1.429)")
    compact_parser.add_argument("--hdepth", type=int, metavar="", default=8, help="Max host depth (default: 8)")
    compact_parser.add_argument("--pdepth", type=int, metavar="", default=9, help="Max path depth (default: 9)")
    compact_parser.set_defaults(func=run_compact)

    lookup_parser = subparsers.add_parser("lookup", help="Look for a SURT into a MementoMap")
    lookup_parser.add_argument("mmap", help="MementoMap file path to look into")
    lookup_parser.add_argument("surt", help="SURT to look for")
    lookup_parser.set_defaults(func=run_lookup)

    batchlookup_parser = subparsers.add_parser("batchlookup", help="Look for a list of SURTs into a MementoMap")
    batchlookup_parser.add_argument("mmap", help="MementoMap file path to look into")
    batchlookup_parser.add_argument("infile", help="Input SURT (plain or GZip) file path or '-' for STDIN")
    batchlookup_parser.set_defaults(func=run_batchlookup)

    args = parser.parse_args()
    try:
        args.func(**vars(args))
    except Exception as e:
        parser.print_help()


if __name__ == "__main__":
    main()
