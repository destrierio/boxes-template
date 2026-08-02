#!/bin/sh
# Plants this run's edge flag, then drops to the service account.
set -e
SEED="${DESTRIER_SEED:-relay-dev-seed}"
printf 'destrier{%s}' "$(printf '%s-edge' "$SEED" | sha256sum | cut -c1-16)" > /home/relay/edge.txt
chown relay:relay /home/relay/edge.txt
chmod 640 /home/relay/edge.txt
exec "$@"
