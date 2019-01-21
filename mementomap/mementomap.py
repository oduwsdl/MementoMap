import sys


class MementoMap():
    """MementoMap is a class that provides methods to interact with and maintain MementoMap files"""

    def __init__(self, debug=False):
        """Initialize a MementoMap instance"""
        self.debug = debug
        self.MAXDEPTHS = {"host": 8, "path": 9}
        # Initialize these with parametrized equations
        self.DEPTHSTATS = {
            "host": [
                (0.99818, 2287.98),
                (0.55153,    8.53),
                (0.17559,    8.95),
                (0.03438,    7.77),
                (0.01534,    6.28),
                (0.00843,    3.42),
                (0.00554,    4.55),
                (0.00229,    1.00)
            ],
            "path": [
                (0.86817,   25.00),
                (0.64156,    7.25),
                (0.35412,    4.96),
                (0.21621,    3.26),
                (0.11310,    3.29),
                (0.05993,    2.70),
                (0.02714,    2.48),
                (0.01237,    2.09),
                (0.00387,    2.01)
            ]
        }


    def compact(self, infile, outfile, cfact=1.0):
        seps = {"host": ",", "path": "/"}
        track = {
            "host": [None]*self.MAXDEPTHS["host"],
            "path": [None]*self.MAXDEPTHS["path"]
        }
        opf = open(outfile, "w")
        with open(infile) as f:
            for line in f:
                surtk, freq, *_ = line.split(maxsplit=2)
                freq = int(freq)
                host, _, path = surtk.partition(")")

                def gen_keys(str, group):
                    parts = str.strip(seps[group]).split(seps[group], self.MAXDEPTHS[group]-1)
                    return [seps[group].join(parts[:i+1]) for i in range(len(parts))]

                keys = {
                    "host": gen_keys(host, "host"),
                    "path": gen_keys(surtk, "path")
                }

                def init_node(group, idx):
                    track[group][idx] = {
                        "key": keys[group][idx],
                        "ccount": 0,
                        "mcount": freq,
                        "optr": opf.tell()
                    }
                    if idx:
                        track[group][idx-1]["ccount"] += 1

                def reset_trail(group, idx):
                    for i in range(idx, self.MAXDEPTHS[group]):
                        if not track[group][i]:
                            break
                        track[group][i] = None

                def compact_subtree(group, idx):
                    for i in range(idx, self.MAXDEPTHS[group]):
                        if not track[group][i]:
                            break
                        if track[group][i]["ccount"] > self.DEPTHSTATS[group][i][1]*cfact:
                            opf.seek(track[group][i]["optr"])
                            opf.truncate()
                            opf.write(f'{track[group][i]["key"]}{seps[group]}* {track[group][i]["mcount"]}\n')
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
                if self.debug:
                    print(f"> {surtk}\t{freq}", file=sys.stderr)
                    print(track, file=sys.stderr)
        opf.close()
