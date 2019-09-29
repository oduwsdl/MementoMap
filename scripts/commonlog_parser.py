#!/usr/bin/env python3

import argparse
import fileinput
import json
import os
import re
import sys
import time

matchers = {
    "clog": re.compile(r'^(?P<host>\S+)\s+(?P<identity>\S+)\s+(?P<user>\S+)\s+\[(?P<origtime>.+?)\]\s+"(?P<request>.*?)"\s+(?P<status>\S+)\s+(?P<size>\S+)(\s+"(?P<referrer>.*?)"\s+"(?P<agent>.*?)"\s*(?P<extras>.*?))?\s*$'),
    "hreq": re.compile(r'^(?P<method>[A-Z]+)\s+([hH][tT]{2}[pP][sS]?://[\w\-\.]+(:\d+)?)?(?P<path>\S+)\s+(?P<httpv>HTTP\/\d(\.\d)?)$'),
    "urim": re.compile(r'^(?P<prefix>[\w\-\/]*?\/)(?P<mtime>\d{14})((?P<rflag>[a-z]{2}_))?\/(?P<urir>\S+)$')
}

validators = {
    "host": re.compile(r'^((25[0-5]|(2[0-4]|1\d?|[2-9])?\d)(\.(25[0-5]|(2[0-4]|1\d?|[2-9])?\d)){3})|([\da-fA-F]{0,4}:){2,7}[\da-fA-F]{0,4}$'),
    "request": re.compile(r'^[A-Z]+\s+\S+\s+HTTP\/\d(\.\d)?$'),
    "status": re.compile(r'^[1-5]\d{2}$'),
    "size": re.compile(r'^\-|\d+$'),
    "referrer": re.compile(r'^(https?://[\w\-\.]+(:\d+)?(/(\S)*)?)?$', re.I)
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
    lines.append(f"Default FORMAT: '{output_format}'")
    return "\n".join(lines)


def parse_record(line, non_empty_fields=[], validate_fields=[], field_matches=[], origtime_format="%d/%b/%Y:%H:%M:%S %z"):
    m = matchers["clog"].match(line)
    if not m:
        raise ValueError("Malformed record")

    record = {fld: "" for fld in formatting_fields}
    record["origline"] = line
    record.update(m.groupdict(default=""))

    for fld in validate_fields:
        reg = validators.get(fld)
        val = record.get(fld, "")
        if reg and not reg.match(val):
            raise ValueError(f"Invalid field {fld}: {val}")

    try:
        et = time.mktime(time.strptime(record["origtime"], origtime_format))
        record["epoch"] = int(et)
        ut = time.gmtime(et)
        record["date"] = time.strftime("%Y-%m-%d", ut)
        record["time"] = time.strftime("%H:%M:%S", ut)
        record["datetime"] = time.strftime("%Y%m%d%H%M%S", ut)
    except Exception as e:
        raise ValueError(f"Invalid time: {record['origtime']}")

    m = matchers["hreq"].match(record["request"])
    if m:
        record.update(m.groupdict(default=""))

    m = matchers["urim"].match(record["path"])
    if m:
        record.update(m.groupdict(default=""))

    for fld in non_empty_fields:
        if record.get(fld, "") in ["", "-"]:
            raise ValueError(f"Empty field: {fld}")

    for (fld, reg) in field_matches:
        val = record.get(fld, "")
        m = reg.search(val)
        if not m:
            raise ValueError(f"Mismatch field {fld}: {val}")

    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage="%(prog)s [options] [FILES ...]", description="A tool to parse Common Log formatted access logs with various derived fields.", epilog=print_fields(), formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-d", "--debug", action="store_true", help="Show debug messages on STDERR")
    parser.add_argument("-n", "--non-empty-fields", metavar="FIELDS", default=[], type=lambda f: [fld.strip() for fld in f.split(",")], help="Skip record if any of the provided fields is empty (comma separated list)")
    parser.add_argument("-v", "--validate-fields", metavar="FIELDS", default=[], type=lambda f: [fld.strip() for fld in f.split(",")], help=f"Skip record if any of the provided field values are invalid ('all' or comma separated list from '{','.join(validators.keys())}')")
    parser.add_argument("-m", "--match-field", metavar="FIELD~RegExp", default=[], action="append", help="Skip record if field does not match the RegExp (can be used multiple times)")
    parser.add_argument("-t", "--origtime-format", metavar="TFORMAT", default=origtime_format, help=f"Original datetime format of logs (default: '{origtime_format.replace('%', '%%')}')")
    parser.add_argument("-f", "--format", default=output_format, help="Output format string (see available formatting fields below)")
    parser.add_argument("-j", "--json", metavar="JFIELDS", default=[], type=lambda f: [fld.strip() for fld in f.split(",")], help="Output NDJSON with the provided fields (use 'all' for all fields except 'origline')")
    parser.add_argument("files", nargs="*", help="Log files (plain/gz/bz2) to parse (reads from the STDIN, if empty or '-')")
    args = parser.parse_args()


    debuglog = sys.stderr
    if not args.debug:
        debuglog = open(os.devnull, "w")

    field_matches = []
    for am in args.match_field:
        fm = am.split("~", 1)
        if len(fm) != 2 or fm[0] not in formatting_fields.keys() or not fm[1]:
            sys.exit(f"'{am}' is not a valid field match option (use 'FIELD~RegEg' instead)")
        try:
            reg = re.compile(fm[1])
            field_matches.append((fm[0], reg))
        except Exception as e:
            sys.exit(f"'{fm[1]}' is not a valid Regular Expression")

    if args.validate_fields == ["all"]:
        args.validate_fields = validators.keys()

    for vf in args.validate_fields:
        if vf not in validators.keys():
            sys.exit(f"'{vf}' field does not have a builtin validation, only '{','.join(validators.keys())}' do")

    for line in fileinput.input(files=args.files, mode="rb", openhook=fileinput.hook_compressed):
        try:
            line = line.decode().strip()
            record = parse_record(line, non_empty_fields=args.non_empty_fields, validate_fields=args.validate_fields, field_matches=field_matches, origtime_format=args.origtime_format)
        except Exception as e:
            print(f"SKIPPING [{e}]: {line}", file=debuglog)
            continue

        try:
            if args.json:
                if args.json == ["all"]:
                    args.json = formatting_fields.keys() - "origline"
                print(json.dumps({fld: record[fld] for fld in args.json}))
            else:
                print(args.format.replace("\\t", "\t").format_map({k: v or "-" for k, v in record.items()}))
        except BrokenPipeError as e:
            sys.exit()
        except KeyError as e:
            sys.exit(f"'{e}' is not a valid formatting field")
