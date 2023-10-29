# main.py
import sqlite3
import os
import subprocess
import logging

logging.basicConfig(level=logging.INFO)

def load_sql_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def create_db_if_not_exists(db_path):
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        conn.close()

def execute_sql_on_db(db_path, sql):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(sql)
    conn.commit()
    conn.close()

db_paths = {
    "knowledge": "/data/knowledge.db",
    "messages": "/data/messages.db",
    "tasks": "/data/tasks.db",
    "conversations": "/data/conversations.db"
}

for db_name, db_path in db_paths.items():
    create_db_if_not_exists(db_path)

    migrations_dir = os.path.join('migrations', db_name)

    if os.path.exists(migrations_dir):
        for file_name in sorted(os.listdir(migrations_dir)):
            if file_name.endswith('.sql'):
                sql_file_path = os.path.join(migrations_dir, file_name)
                sql = load_sql_file(sql_file_path)

                execute_sql_on_db(db_path, sql)

subprocess.run(["datasette", "-h", "0.0.0.0", db_paths["knowledge"], db_paths["messages"], db_paths["tasks"], db_paths["conversations"], "--metadata", "metadata.json", "-p", "5006"])

