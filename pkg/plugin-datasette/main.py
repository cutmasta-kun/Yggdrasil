# main.py
import sqlite3
import os
import subprocess
import logging

# Configurate application
logging.basicConfig(level=logging.INFO)

# Starten von Flask-Server in einem Subprozess
subprocess.run(["python", "flask_server.py"])
