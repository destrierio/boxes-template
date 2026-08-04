"""Ledger — an internal expense tool with a diagnostics page.

The vulnerability is the diagnostics endpoint: it interpolates a user-supplied
host straight into a shell command. A blocklist rejects the two separators
people reach for first, which is the point — the filter is meant to be bypassed
rather than to look absent.
"""

import re
import subprocess

from flask import Flask, request

app = Flask(__name__)

# The naive filter. It rejects `;` and `&`, which stops the most obvious
# payloads, and says nothing about pipes or command substitution.
BLOCKED = re.compile(r"[;&]")

PAGE = """<!doctype html>
<title>Ledger</title>
<h1>Ledger</h1>
<p>Internal expense reconciliation.</p>
<h2>Network diagnostics</h2>
<form method="post" action="/diagnostics">
  <input name="host" placeholder="host to reach" value="127.0.0.1">
  <button type="submit">Check</button>
</form>
"""


@app.get("/")
def index() -> str:
    return PAGE


@app.get("/healthz")
def healthz() -> str:
    return "ok"


@app.post("/diagnostics")
def diagnostics():
    host = request.form.get("host", "").strip()
    if not host:
        return "a host is required", 400
    if BLOCKED.search(host):
        return "the host contains a character that is not permitted", 400

    # The bug. `shell=True` with an interpolated value is the whole challenge;
    # the timeout only keeps a wedged check from holding the worker forever.
    try:
        done = subprocess.run(  # noqa: S602 - deliberate, this is the vulnerability
            f"ping -c 1 -W 1 {host}",
            shell=True,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except subprocess.TimeoutExpired:
        return "the check timed out", 504

    return f"<pre>{done.stdout}{done.stderr}</pre>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)  # noqa: S104 - reachable inside the cell only
