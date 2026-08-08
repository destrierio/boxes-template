#!/bin/sh
set -e

apt-get update
apt-get install -y --no-install-recommends python3
rm -rf /var/lib/apt/lists/*

useradd --create-home --shell /usr/sbin/nologin analyst || true
mkdir -p /opt/signal-desk/files

cat >/opt/signal-desk/files/welcome.txt <<'TXT'
Welcome to Signal Desk.
Shared operator notes are stored in this directory.
TXT

cat >/opt/signal-desk/app.py <<'PY'
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path("/opt/signal-desk/files")
FLAG = "leet{signal_desk_user}"
Path("/opt/signal-desk/flag.txt").write_text(FLAG + "\n")


class Handler(BaseHTTPRequestHandler):
    def write_text(self, status, body):
        self.send_response(status)
        self.send_header("content-type", "text/plain")
        self.end_headers()
        self.wfile.write(body.encode())

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.write_text(
                200,
                "Signal Desk file portal\nTry /download?file=welcome.txt\n",
            )
            return

        if parsed.path == "/health":
            self.write_text(200, "ok\n")
            return

        if parsed.path == "/download":
            requested = parse_qs(parsed.query).get("file", [""])[0]
            if not requested:
                self.write_text(400, "missing file parameter\n")
                return

            target = ROOT / requested
            try:
                self.write_text(200, target.read_text())
            except OSError as error:
                self.write_text(404, f"download failed: {error}\n")
            return

        self.write_text(404, "not found\n")


ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
PY

chown -R analyst:analyst /opt/signal-desk
chmod 750 /opt/signal-desk

cat >/etc/systemd/system/signal-desk.service <<'UNIT'
[Unit]
Description=Signal Desk file portal
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/bin/python3 /opt/signal-desk/app.py
Restart=always
User=analyst

[Install]
WantedBy=multi-user.target
UNIT

systemctl enable signal-desk.service
