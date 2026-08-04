"""The internal service. Not reachable from the entry network at all.

It has no authentication, because it was never meant to be reachable: that
assumption is the challenge. Whoever can send it a request can read the flag.
"""
import os
from flask import Flask

app = Flask(__name__)


@app.get("/")
def index() -> str:
    return "vault: internal inventory service\n"


@app.get("/healthz")
def healthz() -> str:
    return "ok"


@app.get("/records/flag")
def flag() -> str:
    with open("/srv/flag.txt") as fh:
        return fh.read()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)  # noqa: S104
