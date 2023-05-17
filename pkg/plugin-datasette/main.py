# main.py
import sqlite3
import os
import subprocess
import logging

# Configurate application
logging.basicConfig(level=logging.INFO)

# Pfad zur Datenbank
knowledge_db_path = "/data/knowledge.db"
gpt_db_path = "/data/gpt.db"

def check_and_create_db(db_path, create_table_sql=None):
    # Überprüfen, ob die Datenbank existiert
    if not os.path.exists(db_path):
        # Verbindung zur Datenbank herstellen (wird erstellt, wenn sie nicht existiert)
        conn = sqlite3.connect(db_path)

        if create_table_sql:
            logging.info(f"Creating table in {db_path}...")
            # Cursor erstellen
            c = conn.cursor()

            # Tabelle erstellen
            c.execute(create_table_sql)

            # Änderungen speichern
            conn.commit()

        # Verbindung schließen
        conn.close()

# Überprüfen und erstellen Sie die Wissensgraphdatenbank
check_and_create_db(knowledge_db_path)

# Überprüfen und erstellen Sie die GPT-Datenbank und die Nachrichtentabelle
create_table_sql = '''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        message TEXT
    )
'''
check_and_create_db(gpt_db_path, create_table_sql)

# Starten von Flask-Server in einem Subprozess
flask_process = subprocess.Popen(["python", "flask_server.py"])

# Starten von Datasette
subprocess.run(["datasette", "-h", "0.0.0.0", knowledge_db_path, gpt_db_path, "--metadata", "metadata.json"])
