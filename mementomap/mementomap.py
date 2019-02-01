import sys
import re


class MementoMap():
    """MementoMap is a class that provides methods to interact with and maintain MementoMap files"""

    def compact(self, infile, outfile, hcf=1.0, pcf=1.0, ha=16.329, hk=0.714, pa=24.546, pk=1.429, hdepth=8, pdepth=9, debug=False):
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

                def gen_keys(str, layer):
                    parts = str.strip(sep[layer]).split(sep[layer], maxdepth[layer]-1)
                    return [sep[layer].join(parts[:i+1]) for i in range(len(parts))]

                keys = {
                    "host": gen_keys(host, "host"),
                    "path": gen_keys(surtk, "path")
                }

                def init_node(layer, idx):
                    track[layer][idx] = {
                        "key": keys[layer][idx],
                        "ccount": 0,
                        "mcount": freq,
                        "optr": opf.tell()
                    }
                    if idx:
                        track[layer][idx-1]["ccount"] += 1

                def reset_trail(layer, idx):
                    for i in range(idx, maxdepth[layer]):
                        if not track[layer][i]:
                            break
                        track[layer][i] = None

                def compact_subtree(layer, idx):
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
                        init_node("host", i)
                    elif track["host"][i]["key"] == keys["host"][i]:
                        track["host"][i]["mcount"] += freq
                    else:
                        if compact_subtree("host", i):
                            reset_trail("path", 0)
                        reset_trail("host", i)
                        init_node("host", i)
                for i in range(len(keys["path"])):
                    if not track["path"][i]:
                        init_node("path", i)
                    elif track["path"][i]["key"] == keys["path"][i]:
                        track["path"][i]["mcount"] += freq
                    else:
                        compact_subtree("path", i)
                        reset_trail("path", i)
                        init_node("path", i)
                opf.write(line)
                if debug:
                    print(f"> {surtk}\t{freq}", file=sys.stderr)
                    print(track, file=sys.stderr)
        opf.close()


    def lookup(self, infile, surt, debug=False):
        def gen_keys(surt):
            keyre = re.compile(r"(.+)([,/]).+")
            key = surt.split("?")[0].strip("/")
            keys = [key]
            while "," in key:
                m = keyre.match(key)
                keys.append(f"{m[1]}{m[2]}*")
                key = m[1]
            return keys

        def bin_search(infile, key, debug=False):
            with open(infile, "rb") as f:
                surtk, freq, *_ = f.readline().split(maxsplit=2)
                if debug:
                    print(f"Matching FIRST> {key} {surtk} {freq}", file=sys.stderr)
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
                    if debug:
                        print(f"Matching {left}:{mid}:{right}> {key} {surtk} {freq}", file=sys.stderr)
                    if key == surtk:
                        return [surtk, freq]
                    elif key > surtk:
                        left = mid
                    else:
                        right = mid

        for k in gen_keys(surt):
            if debug:
                print(f"Searching> {k}", file=sys.stderr)
            res = bin_search(infile, k.encode(), debug=debug)
            if res:
                return [i.decode() for i in res]
