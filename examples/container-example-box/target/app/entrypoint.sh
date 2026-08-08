#!/bin/sh
# Runs as root only long enough to place the runtime flag, set its permissions,
# then drop privileges before starting the application.
set -e

default_flag() {
  seed="${DESTRIER_SEED:-example-seed}"
  printf 'destrier{%s}' "$(printf '%s:bulletin:app:service-user' "$seed" | sha256sum | cut -c1-16)"
}

FLAG="${DESTRIER_FLAG_APP_SERVICE_USER:-$(default_flag)}"

printf '%s\n' "$FLAG" > /flag.txt
chown web:web /flag.txt
chmod 640 /flag.txt

exec "$@"
