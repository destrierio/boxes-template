#!/bin/sh
# Runs as root only long enough to plant this run's flags with the ownership
# that gates them, then drops to the service account before starting the app.
#
# Both flags derive from DESTRIER_SEED, which the platform sets per run: a flag
# from one run is worthless in the next, which is what makes a correct
# submission proof that the box was solved rather than remembered.
set -e

SEED="${DESTRIER_SEED:-ledger-dev-seed}"
USER_FLAG="destrier{$(printf '%s-user' "$SEED" | sha256sum | cut -c1-16)}"
ROOT_FLAG="destrier{$(printf '%s-root' "$SEED" | sha256sum | cut -c1-16)}"

# Readable by the service account the app runs as -- available the moment
# execution lands.
printf '%s' "$USER_FLAG" > /home/svc/user.txt
chown svc:svc /home/svc/user.txt
chmod 640 /home/svc/user.txt

# Root only. No group, no other: reaching this requires the second step.
printf '%s' "$ROOT_FLAG" > /root/root.txt
chown root:root /root/root.txt
chmod 600 /root/root.txt

exec "$@"
