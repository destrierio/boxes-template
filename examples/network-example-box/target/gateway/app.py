"""
Relay Yard gateway.

Intentionally vulnerable (CWE-918, server-side request forgery). The `/fetch`
endpoint fetches an arbitrary URL from the gateway host, which is attached to
both the external and internal networks.
"""
from urllib.parse import urlparse

import requests
from flask import Flask, Response, request

app = Flask(__name__)

INDEX = """<!doctype html>
<html>
  <head><title>Relay Yard</title></head>
  <body>
    <h1>Relay Yard Gateway</h1>
    <p>Internal URL fetch utility.</p>
    <p>Use <code>GET /fetch?url=http://example.internal/</code> to retrieve a URL.</p>
  </body>
</html>
"""


@app.route("/")
def index():
    return INDEX


@app.route("/fetch")
def fetch():
    raw_url = request.args.get("url", "")
    if not raw_url:
        return Response("missing 'url' parameter\n", status=400, mimetype="text/plain")

    parsed = urlparse(raw_url)
    if parsed.scheme not in {"http", "https"}:
        return Response("only http and https URLs are supported\n", status=400, mimetype="text/plain")

    try:
        response = requests.get(raw_url, timeout=3)
    except requests.RequestException as error:
        return Response(f"fetch failed: {error}\n", status=502, mimetype="text/plain")

    content_type = response.headers.get("content-type", "text/plain")
    return Response(response.content, status=response.status_code, content_type=content_type)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
