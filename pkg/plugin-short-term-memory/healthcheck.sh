#!/bin/sh
# healthcheck.sh

# Überprüfen, ob main.py läuft
pgrep -f 'main.py' > /dev/null
pgrep_status=$?

if [ $pgrep_status -ne 0 ]; then
    exit 1
fi

exit 0
