#!/usr/bin/env python3

import sys

from mementomap.mementomap import MementoMap


if __name__ == "__main__":
    debug = False
    if len(sys.argv) > 4:
        debug = True
    if len(sys.argv) < 4:
        print(f"Usage:\n  {sys.argv[0]} <infile:path> <outfile:path> <cfact:float> [--debug]", file=sys.stderr)
        sys.exit(1)

    mm = MementoMap(debug=debug)
    mm.compact(sys.argv[1], sys.argv[2], cfact=float(sys.argv[3]))
