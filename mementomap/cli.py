import locale
import re

locale.setlocale(locale.LC_ALL, 'C')


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
    counts = {"inlines": 0, "outlines": 0, "inbytes": 0, "outbytes": 0, "rollups": 0}

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
        compacted = False
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
                counts["rollups"] += 1
                compacted = True
                break
        _reset_trail(layer, idx)
        if layer == "host":
            if compacted:
                _reset_trail("path", 0)
            else:
                _compact_subtree("path", 0)

    opf = open(outfile, "wb")
    for line in infiter:
        counts["inlines"] += 1
        counts["inbytes"] += len(line)
        if line[0] == b"!":
            opf.write(line)
            counts["outlines"] += 1
            continue
        try:
            parts = line.split(maxsplit=2)
            surtk = parts[0].split(b"?")[0].strip(b"/,")
            freq = int(parts[1])
        except Exception as e:
            continue
        if b"," not in surtk:
            continue
        host, _, path = surtk.partition(b")")
        keys = {
            "host": _gen_keys(host, "host"),
            "path": _gen_keys(surtk, "path")
        }

        for layer in ["host", "path"]:
            for i in range(len(keys[layer])):
                if not trail[layer][i]:
                    _init_node(layer, i)
                elif trail[layer][i]["key"] == keys[layer][i]:
                    trail[layer][i]["mcount"] += freq
                else:
                    _compact_subtree(layer, i)
                    _init_node(layer, i)

        opf.write(surtk + b" %d\n" % freq)
        counts["outlines"] += 1
    _compact_subtree("host", 0)
    _compact_subtree("path", 0)
    opf.truncate()
    counts["outbytes"] += opf.tell()
    opf.close()
    return counts


def cdx2hxpx(infiter):
    key = None
    count = 0
    for line in infiter:
        try:
            surtk = line.split(maxsplit=1)[0].split(b"?")[0].strip(b"/,")
        except Exception as e:
            continue
        if b")" not in surtk:
            surtk = None
        if key == surtk:
            count += 1
        if key != surtk:
            if key:
                yield key + b" %d" % count
            key = surtk
            count = 1
    if key:
        yield key + b" %d" % count


def generate(infiter, outfile, hcf=float("inf"), pcf=float("inf"), **kw):
    hxpx = cdx2hxpx(infiter)
    return compact(hxpx, outfile, hcf, pcf, **kw)


def bin_search(mmapiter, key):
    surtk, freq, *_ = mmapiter.readline().split(maxsplit=2)
    if key == surtk:
        return [surtk, freq]
    left = 0
    mmapiter.seek(0, 2)
    right = mmapiter.tell()
    while (right - left > 1):
        mid = (right + left) // 2
        mmapiter.seek(mid)
        mmapiter.readline()
        surtk, freq, *_ = mmapiter.readline().split(maxsplit=2)
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
        if key.endswith(")"):
            keys.append(key.strip(")") + ",*")
        try:
            m = keyre.match(key)
            keys.append(f"{m[1]}{m[2]}*")
            key = m[1]
        except Exception as e:
            key = key.strip("/,")
    return keys


def lookup(mmapiter, surt, **kw):
    for idx, key in enumerate(lookup_keys(surt)):
        res = bin_search(mmapiter, key.encode())
        if res:
            return {"surtk": res[0].decode(), "freq": res[1].decode(), "dist": str(idx), "surt": surt}
