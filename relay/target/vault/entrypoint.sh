#!/bin/sh
# Runs as root only long enough to plant this run's flag with the ownership
# that gates it, then drops to the service account.
set -e
# The platform mints this run's flag and tells us what to plant. One
# direction: no derivation rule for the platform to reproduce, and nothing
# for it to discover afterwards. The fallback is dev-only -- a run always
# sets it, and a box that quietly used a fixed flag in production would
# make every previous run's answer valid forever.
FLAG="${DESTRIER_FLAG:-destrier{local-dev-only-flag}}"
printf '%s' "$FLAG" > /srv/flag.txt
chown vault:vault /srv/flag.txt
chmod 640 /srv/flag.txt
exec "$@"
