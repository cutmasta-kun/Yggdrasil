# main.py
import sqlite3
import os
import subprocess
import logging

# Configurate application
logging.basicConfig(level=logging.INFO)

def load_sql_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def create_db_if_not_exists(db_path):
    # Überprüfen, ob die Datenbank existiert
    if not os.path.exists(db_path):
        # Verbindung zur Datenbank herstellen (wird erstellt, wenn sie nicht existiert)
        conn = sqlite3.connect(db_path)
        # Verbindung schließen
        conn.close()

def execute_sql_on_db(db_path, sql):
    # Verbindung zur Datenbank herstellen
    conn = sqlite3.connect(db_path)
    # Cursor erstellen
    c = conn.cursor()
    # SQL ausführen
    c.execute(sql)
    # Änderungen speichern
    conn.commit()
    # Verbindung schließen
    conn.close()

# Pfad zur Datenbank
db_paths = {
    "knowledge": "/data/knowledge.db",
    "messages": "/data/messages.db",
    "tasks": "/data/tasks.db"
}

# Überprüfen und erstellen Sie die Datenbanken
for db_name, db_path in db_paths.items():
    # Erstellen Sie das Datenbank-Datei, falls es noch nicht existiert
    create_db_if_not_exists(db_path)

    # Pfad zum Migrationsverzeichnis für diese Datenbank
    migrations_dir = os.path.join('migrations', db_name)

    # Überprüfen Sie, ob das Migrationsverzeichnis existiert
    if os.path.exists(migrations_dir):
        # Durchlaufen Sie alle .sql Dateien im Migrationsverzeichnis
        for file_name in sorted(os.listdir(migrations_dir)):
            if file_name.endswith('.sql'):
                sql_file_path = os.path.join(migrations_dir, file_name)
                sql = load_sql_file(sql_file_path)

                # Führen Sie die Migration aus
                execute_sql_on_db(db_path, sql)

# Starten von Datasette
subprocess.run(["datasette", "-h", "0.0.0.0", db_paths["knowledge"], db_paths["messages"], db_paths["tasks"], "--metadata", "metadata.json"])

