#!/bin/sh
# runs as root only long enough to generate the per-run flag, set its
# permissions, then drop privileges before starting the application.
set -e

SEED="${DESTRIER_SEED:-example-seed}"
FLAG="destrier{$(printf '%s' "$SEED" | sha256sum | cut -c1-16)}"

printf '%s' "$FLAG" > /flag.txt
chown web:web /flag.txt
chmod 640 /flag.txt

exec "$@"