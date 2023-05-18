#!/bin/bash

# Warte, bis die Umgebungsvariable LISTEN_TOPIC verfügbar ist
while [[ -z "${LISTEN_TOPIC}" ]]; do
  sleep 1
done

# Warte, bis der Function Webservice verfügbar ist
while ! curl -s "http://function:5000" > /dev/null; do
  echo 'Waiting for function...'
  sleep 1
done

echo 'Function is up - starting communication-app'

# Starte das Python-Skript
python -u main.py
