# Dockerfile

FROM python:slim

RUN apt-get update && \
    apt-get install -y wget gnupg curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Kopieren der Abhängigkeiten
COPY pkg/communication/main.py /app/
COPY pkg/communication/logger.py /app/
COPY pkg/communication/entrypoint.sh /app
RUN chmod +x /app/entrypoint.sh

# Installieren der Python Abhängigkeiten
RUN pip install requests

# Setzen des Arbeitsverzeichnisses
WORKDIR /app

# Healthcheck zur Überprüfung, ob der Startprozess läuft
HEALTHCHECK  --interval=5s --timeout=3s --start-period=10s \
  CMD pgrep -f "main.py" || (python logger.py "... Communication System failed: No Topics to listen to" && exit 1)

# Standardkommando, das beim Start des Containers ausgeführt wird
CMD ["/app/entrypoint.sh"]
