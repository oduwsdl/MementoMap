#!/usr/bin/env python3

import sys

from mementomap.mementomap import MementoMap


if __name__ == "__main__":
    debug = False

    def print_help():
        print(f"Usage:\n  {sys.argv[0]} lookup <infile:path> <key:surt>\n  {sys.argv[0]} compact <infile:path> <outfile:path> <hcf:float> <pcf:float> [--debug]", file=sys.stderr)
        sys.exit(1)

    if "--debug" in sys.argv:
        debug = True

    if len(sys.argv) < 2 or (sys.argv[1] == "compact" and len(sys.argv) < 6) or (sys.argv[1] == "lookup" and len(sys.argv) < 4):
        print_help()

    mm = MementoMap(debug=debug)
    if sys.argv[1] == "compact":
        mm.compact(sys.argv[2], sys.argv[3], hcf=float(sys.argv[4]), pcf=float(sys.argv[5]))
    elif sys.argv[1] == "lookup":
        res = mm.lookup(sys.argv[2], sys.argv[3])
        if res:
            print(" ".join(res))
