#!/usr/bin/env python3

from mementomap.mementomap import MementoMap


if __name__ == "__main__":
    mm = MementoMap(debug=True)
    mm.compact("samples/sample-01.ukvs", cfact=0.9)
