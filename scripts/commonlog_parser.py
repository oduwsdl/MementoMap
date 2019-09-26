#!/usr/bin/env python3

import argparse
import fileinput
import os
import re
import sys
import time

patterns = {
    "clog": re.compile(r'^(?P<host>\S+)\s+(?P<identity>\S+)\s+(?P<user>\S+)\s+\[(?P<origtime>.+?)\]\s+"(?P<request>.*?)"\s+(?P<status>\S+)\s+(?P<size>\S+)(\s+"(?P<referrer>.*?)"\s+"(?P<agent>.*?)"\s*(?P<extras>.*?))?\s*$'),
    "hreq": re.compile(r'^(?P<method>[A-Z]+)\s+(https?://[\w\-\.]+)?(?P<path>\S+)\s+(?P<httpv>\S+)$'),
    "urim": re.compile(r'^(?P<prefix>[\w\-\/]*?\/)(?P<mtime>\d{14})((?P<rflag>[a-z]{2}_))?\/(?P<urir>\S+)$')
}

origtime_format = "%d/%b/%Y:%H:%M:%S %z"
output_format = '{host} {date} {time} {method} {path} {status} {size} "{referrer}" "{agent}"'

formatting_fields = {
    "origline": "Original log line",
    "host": "IP address of the client",
    "identity": "Identity of the client, usually '-'",
    "user": "User ID for authentication, usually '-'",
    "origtime": "Original date and time (typically in '%d/%b/%Y:%H:%M:%S %z' format)",
    "epoch": "Seconds from the Unix epoch (derived from origtime)",
    "date": "UTC date in '%Y-%m-%d' format (derived from origtime)",
    "time": "UTC time in '%H:%M:%S' format (derived from origtime)",
    "datetime": "14 digit datetime in '%Y%m%d%H%M%S' format (derived from origtime)",
    "request": "Original HTTP request line",
    "method": "HTTP method (empty for invalid request)",
    "path": "Path and query (scheme and host removed, empty for invalid request)",
    "prefix": "Memento endpoint path prefix (derived from path)",
    "mtime": "14 digit Memento datetime (derived from path)",
    "rflag": "Memento rewrite flag (derived from path)",
    "urir": "Memento URI-R (derived from path)",
    "httpv": "HTTP version (empty for invalid request)",
    "status": "Returned status code",
    "size": "Number of bytes returned",
    "referrer": "Referer header (empty, if not logged)",
    "agent": "User-agent header (empty, if not logged)",
    "extras": "Any additional logged fields"
}


def print_fields():
    lines = ["formatting fields:"]
    for fld, desc in formatting_fields.items():
        fld = f"{{{fld}}}"
        lines.append(f"  {fld:21} {desc}")
    lines.append(f"default FORMAT: '{output_format}'")
    return "\n".join(lines)


def parse_record(line, non_empty_fields=[], origtime_format="%d/%b/%Y:%H:%M:%S %z"):
    m = patterns["clog"].match(line)
    if not m:
        raise ValueError("Malformed record")

    record = {fld: "" for fld in formatting_fields}
    record["origline"] = line
    record.update(m.groupdict(default=""))

    try:
        et = time.mktime(time.strptime(record["origtime"], origtime_format))
        record["epoch"] = int(et)
        ut = time.gmtime(et)
        record["date"] = time.strftime("%Y-%m-%d", ut)
        record["time"] = time.strftime("%H:%M:%S", ut)
        record["datetime"] = time.strftime("%Y%m%d%H%M%S", ut)
    except Exception as e:
        raise ValueError(f"Invalid time: {record['origtime']}")

    m = patterns["hreq"].match(record["request"])
    if m:
        record.update(m.groupdict(default=""))
    if not record["method"]:
        raise ValueError(f"Invalid request: {record['request']}")

    m = patterns["urim"].match(record["path"])
    if m:
        record.update(m.groupdict(default=""))

    for fld in non_empty_fields:
        if record.get(fld, "") in ["", "-"]:
            raise ValueError(f"Empty field: {fld}")

    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A tool to parse Common Log formatted access logs with various derived fields.", epilog=print_fields(), formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-d", "--debug", action="store_true", help="Show debug messages on STDERR")
    parser.add_argument("-e", "--empty-skip", metavar="FIELDS", default=[], type=lambda f: [fld.strip() for fld in f.split(",")], help="Skip record if any of these fields is empty (comma separated list)")
    parser.add_argument("-t", "--origtime-format", metavar="TFORMAT", default=origtime_format, help=f"Original datetime format of logs (default: '{origtime_format.replace('%', '%%')}')")
    parser.add_argument("-f", "--format", default=output_format, help="Output format string")
    parser.add_argument("files", nargs="*", help="One or more log files (plain, gz, or bz2) to parse\n(reads from the STDIN, if empty or '-')")
    args = parser.parse_args()


    debuglog = sys.stderr
    if not args.debug:
        debuglog = open(os.devnull, "w")

    for line in fileinput.input(files=args.files, mode="rb", openhook=fileinput.hook_compressed):
        try:
            line = line.decode().strip()
            record = parse_record(line, non_empty_fields=args.empty_skip, origtime_format=args.origtime_format)
        except Exception as e:
            print(f"SKIPPING [{e}]: {line}", file=debuglog)
            continue

        try:
            print(args.format.replace("\\t", "\t").format_map({k: v or "-" for k, v in record.items()}))
        except BrokenPipeError as e:
            sys.exit()
        except KeyError as e:
            sys.exit(f"{e} is not a valid format option")
