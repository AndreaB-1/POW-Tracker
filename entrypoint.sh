#!/bin/sh
# Fix ownership of the bind-mounted /data directory, then drop to non-root user.
# This runs as root so the compose file needs no host-side chown.
chown solartrack:solartrack /data
exec gosu solartrack "$@"
