import re


def compact(infiter, outfile, hcf=1.0, pcf=1.0, ha=16.329, hk=0.714, pa=24.546, pk=1.429, hdepth=8, pdepth=9, **kw):
    sep = {"host": b",", "path": b"/"}
    maxdepth = {"host": hdepth, "path": pdepth}
    cutoff = {
        "host": [ha * (i+1) ** -hk * hcf for i in range(maxdepth["host"])],
        "path": [pa * (i+1) ** -pk * pcf for i in range(maxdepth["path"])]
    }
    trail = {
        "host": [None]*maxdepth["host"],
        "path": [None]*maxdepth["path"]
    }
    counts = {"inlines": 0, "outlines": 0}

    def _gen_keys(str, layer):
        parts = str.strip(sep[layer]).split(sep[layer], maxdepth[layer]-1)
        return [sep[layer].join(parts[:i+1]) for i in range(len(parts))]

    def _init_node(layer, idx):
        trail[layer][idx] = {
            "key": keys[layer][idx],
            "ccount": 0,
            "mcount": freq,
            "optr": opf.tell(),
            "oline": counts["outlines"]
        }
        if idx:
            trail[layer][idx-1]["ccount"] += 1

    def _reset_trail(layer, idx):
        for i in range(idx, maxdepth[layer]):
            if not trail[layer][i]:
                break
            trail[layer][i] = None

    def _compact_subtree(layer, idx):
        for i in range(idx, maxdepth[layer]):
            if not trail[layer][i]:
                break
            if not i and layer == "host":
                continue
            if trail[layer][i]["ccount"] > cutoff[layer][i]:
                opf.seek(trail[layer][i]["optr"])
                counts["outlines"] = trail[layer][i]["oline"]
                opf.write(trail[layer][i]["key"] + sep[layer] + b"* %d\n" % trail[layer][i]["mcount"])
                counts["outlines"] += 1
                break

    opf = open(outfile, "wb")
    for line in infiter:
        counts["inlines"] += 1
        if line[0] == b"!":
            opf.write(line)
            counts["outlines"] += 1
            continue
        parts = line.split(maxsplit=2)
        surtk = parts[0].strip(b"/,")
        freq = int(parts[1])
        host, _, path = surtk.partition(b")")
        keys = {
            "host": _gen_keys(host, "host"),
            "path": _gen_keys(surtk, "path")
        }

        for i in range(len(keys["host"])):
            if not trail["host"][i]:
                _init_node("host", i)
            elif trail["host"][i]["key"] == keys["host"][i]:
                trail["host"][i]["mcount"] += freq
            else:
                _compact_subtree("host", i)
                _reset_trail("host", i)
                _compact_subtree("path", 0)
                _reset_trail("path", 0)
                _init_node("host", i)
        for i in range(len(keys["path"])):
            if not trail["path"][i]:
                _init_node("path", i)
            elif trail["path"][i]["key"] == keys["path"][i]:
                trail["path"][i]["mcount"] += freq
            else:
                _compact_subtree("path", i)
                _reset_trail("path", i)
                _init_node("path", i)
        opf.write(surtk + b" %d\n" % freq)
        counts["outlines"] += 1
    _compact_subtree("host", 0)
    _compact_subtree("path", 0)
    opf.truncate()
    opf.close()
    return counts


def bin_search(mmap, key):
    with open(mmap, "rb") as f:
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
    keys = [key, f"{key}/*"]
    while "," in key:
        m = keyre.match(key)
        keys.append(f"{m[1]}{m[2]}*")
        key = m[1]
    return keys


def lookup(mmap, surt, **kw):
    for k in lookup_keys(surt):
        res = bin_search(mmap, k.encode())
        if res:
            return [i.decode() for i in res]
