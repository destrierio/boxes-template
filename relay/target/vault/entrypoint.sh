#!/bin/sh
# Runs as root only long enough to plant this run's flag with the ownership
# that gates it, then drops to the service account.
set -e
SEED="${DESTRIER_SEED:-relay-dev-seed}"
printf 'destrier{%s}' "$(printf '%s-vault' "$SEED" | sha256sum | cut -c1-16)" > /srv/flag.txt
chown vault:vault /srv/flag.txt
chmod 640 /srv/flag.txt
exec "$@"
