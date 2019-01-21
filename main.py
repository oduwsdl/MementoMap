#!/usr/bin/env python3

import sys

from mementomap.mementomap import MementoMap


if __name__ == "__main__":
    debug = False
    if len(sys.argv) > 5:
        debug = True
    if len(sys.argv) < 5:
        print(f"Usage:\n  {sys.argv[0]} <infile:path> <outfile:path> <hcf:float> <pcf:float> [--debug]", file=sys.stderr)
        sys.exit(1)

    mm = MementoMap(debug=debug)
    mm.compact(sys.argv[1], sys.argv[2], hcf=float(sys.argv[3]), pcf=float(sys.argv[4]))
