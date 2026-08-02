"""Relay — a link-preview service on the edge of the network.

The preview endpoint fetches whatever URL it is given. A blocklist stops the
obvious loopback spellings, which is the point: it is meant to be stepped
around, and what lies past it is a network the caller cannot reach directly.
"""
import re
import urllib.request

from flask import Flask, request

app = Flask(__name__)

# Rejects the loopback spellings people try first. Says nothing about the rest
# of the internal network -- which is where the interesting service lives.
BLOCKED = re.compile(r"(localhost|127\.0\.0\.1|0\.0\.0\.0|\[::1\])", re.I)

PAGE = """<!doctype html>
<title>Relay</title>
<h1>Relay</h1>
<p>Link previews for the intranet.</p>
<form method="get" action="/preview">
  <input name="url" placeholder="https://example.internal/page" size="48">
  <button type="submit">Preview</button>
</form>
"""


@app.get("/")
def index() -> str:
    return PAGE


@app.get("/healthz")
def healthz() -> str:
    return "ok"


@app.get("/preview")
def preview():
    url = request.args.get("url", "").strip()
    if not url:
        return "a url is required", 400
    if BLOCKED.search(url):
        return "that host is not permitted", 400
    # No scheme restriction. The handler was written against "a URL is a web
    # page", so whatever else the fetcher happens to support came along with
    # it -- which is the first half of the box.

    # The bug: the fetch happens from this host, which sits on both networks.
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:  # noqa: S310
            body = resp.read(65536).decode("utf-8", "replace")
    except Exception as exc:  # surfaced so the caller can map the network
        return f"<pre>fetch failed: {exc}</pre>", 502
    return f"<pre>{body}</pre>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)  # noqa: S104
