# Verwenden Sie das offizielle Python-Image als Basis
FROM python:3.8.17-slim

# Installieren Sie die benötigten Systembibliotheken
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y v4l2loopback-dkms

# Setzen Sie das Arbeitsverzeichnis
WORKDIR /app

# Kopieren Sie die Anforderungsdatei in das Arbeitsverzeichnis
COPY requirements.txt .

# Installieren Sie die Python-Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Kopieren Sie das Python-Skript in das Arbeitsverzeichnis
COPY main.py .

# Führen Sie das Python-Skript aus
CMD ["python", "-u", "main.py"]
