#!/bin/sh
set -e

apt-get update
apt-get install -y --no-install-recommends python3
rm -rf /var/lib/apt/lists/*

useradd --create-home --shell /usr/sbin/nologin analyst || true
mkdir -p /opt/relay-yard

cat >/opt/relay-yard/internal_api.py <<'PY'
import hashlib
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SEED = os.environ.get("DESTRIER_SEED", "relay-yard-seed")
DEFAULT_FLAG = f"destrier{{{hashlib.sha256(f'{SEED}:relay-yard:workstation:user'.encode()).hexdigest()[:16]}}}"
FLAG = os.environ.get("DESTRIER_FLAG_WORKSTATION_USER", DEFAULT_FLAG)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok\n")
            return

        if self.path == "/flag":
            self.send_response(200)
            self.end_headers()
            self.wfile.write((FLAG + "\n").encode())
            return

        self.send_response(404)
        self.end_headers()


ThreadingHTTPServer(("0.0.0.0", 8001), Handler).serve_forever()
PY

cat >/etc/systemd/system/relay-yard-internal.service <<'UNIT'
[Unit]
Description=Relay Yard internal workstation API
After=network-online.target
Wants=network-online.target

[Service]
Environment=DESTRIER_SEED=relay-yard-seed
EnvironmentFile=-/etc/destrier/flags.env
ExecStart=/usr/bin/python3 /opt/relay-yard/internal_api.py
Restart=always
User=analyst

[Install]
WantedBy=multi-user.target
UNIT

systemctl enable relay-yard-internal.service
