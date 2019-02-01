import sys
import re


def compact(infile, outfile, hcf=1.0, pcf=1.0, ha=16.329, hk=0.714, pa=24.546, pk=1.429, hdepth=8, pdepth=9):
    sep = {"host": ",", "path": "/"}
    maxdepth = {"host": hdepth, "path": pdepth}
    cutoff = {
        "host": [ha * (i+1) ** -hk * hcf for i in range(maxdepth["host"])],
        "path": [pa * (i+1) ** -pk * pcf for i in range(maxdepth["path"])]
    }
    track = {
        "host": [None]*maxdepth["host"],
        "path": [None]*maxdepth["path"]
    }
    opf = open(outfile, "w")
    with open(infile) as f:
        for line in f:
            surtk, freq, *_ = line.split(maxsplit=2)
            freq = int(freq)
            host, _, path = surtk.partition(")")

            def _gen_keys(str, layer):
                parts = str.strip(sep[layer]).split(sep[layer], maxdepth[layer]-1)
                return [sep[layer].join(parts[:i+1]) for i in range(len(parts))]

            keys = {
                "host": _gen_keys(host, "host"),
                "path": _gen_keys(surtk, "path")
            }

            def _init_node(layer, idx):
                track[layer][idx] = {
                    "key": keys[layer][idx],
                    "ccount": 0,
                    "mcount": freq,
                    "optr": opf.tell()
                }
                if idx:
                    track[layer][idx-1]["ccount"] += 1

            def _reset_trail(layer, idx):
                for i in range(idx, maxdepth[layer]):
                    if not track[layer][i]:
                        break
                    track[layer][i] = None

            def _compact_subtree(layer, idx):
                for i in range(idx, maxdepth[layer]):
                    if not track[layer][i]:
                        break
                    if not i and layer == "host":
                        continue
                    if track[layer][i]["ccount"] > cutoff[layer][i]:
                        opf.seek(track[layer][i]["optr"])
                        opf.truncate()
                        opf.write(f'{track[layer][i]["key"]}{sep[layer]}* {track[layer][i]["mcount"]}\n')
                        return True

            for i in range(len(keys["host"])):
                if not track["host"][i]:
                    _init_node("host", i)
                elif track["host"][i]["key"] == keys["host"][i]:
                    track["host"][i]["mcount"] += freq
                else:
                    if _compact_subtree("host", i):
                        _reset_trail("path", 0)
                    _reset_trail("host", i)
                    _init_node("host", i)
            for i in range(len(keys["path"])):
                if not track["path"][i]:
                    _init_node("path", i)
                elif track["path"][i]["key"] == keys["path"][i]:
                    track["path"][i]["mcount"] += freq
                else:
                    _compact_subtree("path", i)
                    _reset_trail("path", i)
                    _init_node("path", i)
            opf.write(line)
    opf.close()


def bin_search(infile, key):
    with open(infile, "rb") as f:
        surtk, freq, *_ = f.readline().split(maxsplit=2)
        if key == surtk:
            return [surtk, freq]
        left = 0
        f.seek(0, 2)
        right = f.tell()
        while (right - left > 1):
            mid = (right + left) // 2
            f.seek(mid)
            f.readline()
            surtk, freq, *_ = f.readline().split(maxsplit=2)
            if key == surtk:
                return [surtk, freq]
            elif key > surtk:
                left = mid
            else:
                right = mid


def lookup_keys(surt):
    keyre = re.compile(r"(.+)([,/]).+")
    key = surt.split("?")[0].strip("/")
    keys = [key]
    while "," in key:
        m = keyre.match(key)
        keys.append(f"{m[1]}{m[2]}*")
        key = m[1]
        return keys


def lookup(infile, surt):
    for k in lookup_keys(surt):
        res = bin_search(infile, k.encode())
        if res:
            return [i.decode() for i in res]
