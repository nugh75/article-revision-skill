#!/usr/bin/env python3
"""Capture or locate the exact original Markdown span of a revision sidecar."""

import argparse
import hashlib
import re
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("capture", "locate"))
    parser.add_argument("article", type=Path)
    parser.add_argument("lines", help="Original inclusive START:END line range")
    parser.add_argument("fingerprint", nargs="?", help="SHA-256 recorded at capture")
    args = parser.parse_args()
    bounds = re.fullmatch(r"([1-9]\d*):([1-9]\d*)", args.lines)
    if not bounds:
        parser.error("use the START:END line range")
    start, end = map(int, bounds.groups())
    if start > end:
        parser.error("the end line must follow the start line")

    source = args.article.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    lines = source.splitlines(keepends=True)
    if args.action == "capture":
        if end > len(lines):
            parser.error("line range exceeds the article")
        print(hashlib.sha256(b"".join(lines[start - 1:end])).hexdigest())
        return 0

    if not args.fingerprint or not re.fullmatch(r"[a-f0-9]{64}", args.fingerprint):
        parser.error("locate requires the recorded SHA-256")
    length = end - start + 1
    found = None
    for offset in range(len(lines) - length + 1):
        if hashlib.sha256(b"".join(lines[offset:offset + length])).hexdigest() != args.fingerprint:
            continue
        if found is not None:
            print("Parte originale ambigua: più intervalli hanno la stessa impronta.", file=sys.stderr)
            return 1
        found = f"{offset + 1}:{offset + length}"
    if found is None:
        print("Parte originale cambiata o assente nell'articolo attivo.", file=sys.stderr)
        return 1
    print(found)
    return 0


if __name__ == "__main__":
    sys.exit(main())
