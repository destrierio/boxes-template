#!/bin/sh
# Runs as root only long enough to place the static flag, set its permissions,
# then drop privileges before starting the application.
set -e

printf '%s\n' 'destrier{bul1371n_53rv1c3_f1l3_r34d}' > /flag.txt
chown web:web /flag.txt
chmod 640 /flag.txt

exec "$@"
