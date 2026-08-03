#!/bin/sh
# Runs as root only long enough to plant this run's flags with the ownership
# that gates them, then drops to the service account before starting the app.
#
# The platform mints both flags for this run and tells us what to plant. A flag
# from one run is worthless in the next, which is what makes a correct
# submission proof the box was solved rather than remembered.
#
# By id, not a bare DESTRIER_FLAG: this host holds two flags at two privilege
# levels, and the platform deliberately sends no default here so the root flag
# cannot end up in the user's file.
set -e

USER_FLAG="${DESTRIER_FLAG_USER:-destrier{local-dev-user}}"
ROOT_FLAG="${DESTRIER_FLAG_ROOT:-destrier{local-dev-root}}"

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
