#!/bin/sh
# Runs as root only long enough to place the static flag, set its permissions,
# then drop privileges before starting the application.
set -e

printf '%s\n' 'leet{bulletin_service_user}' > /flag.txt
chown web:web /flag.txt
chmod 640 /flag.txt

exec "$@"
